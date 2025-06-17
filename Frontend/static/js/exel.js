import * as XLSX from 'xlsx';

// Data structure classes
class Product {
    constructor(sku, name, weight, features) {
        this.sku = sku;
        this.name = name;
        this.weight = weight;
        this.features = features;
    }
}

class Warehouse {
    constructor(id, name, address, metadata) {
        this.id = id;
        this.name = name;
        this.address = address;
        this.metadata = metadata;
        this.cargos = []; // Will be populated from inventory
    }
}

class InventoryItem {
    constructor(warehouseId, productSku, quantity) {
        this.warehouseId = warehouseId;
        this.productSku = productSku;
        this.quantity = quantity;
    }
}

class Destination {
    constructor(id, name, address, productSku, requiredQuantity) {
        this.id = id;
        this.name = name;
        this.address = address;
        this.productSku = productSku;
        this.requiredQuantity = requiredQuantity;
        this.cargos = [{type: productSku, quantity: requiredQuantity}];
    }
}

class Transport {
    constructor(id, name, maxLoad, fuelConsumption) {
        this.id = id;
        this.name = name;
        this.maxLoad = maxLoad;
        this.fuelConsumption = fuelConsumption;
    }
}

class TransportTaskData {
    constructor() {
        this.products = [];
        this.warehouses = [];
        this.inventory = [];
        this.destinations = [];
        this.transports = [];
    }

    async loadFromExcel(file) {
        const statusElement = document.getElementById('load-status');
        statusElement.textContent = 'Загрузка данных из Excel...';
        statusElement.style.color = 'blue';
        
        try {
            const data = await file.arrayBuffer();
            const workbook = XLSX.read(data);
            
            // Load products
            const productsSheet = workbook.Sheets['Товары'];
            const productsData = XLSX.utils.sheet_to_json(productsSheet);
            this.products = productsData.map(row => new Product(
                String(row['SKU']),
                row['Название'],
                parseFloat(row['Вес (кг)']),
                row['Особенности'] || ''
            ));
            
            // Load warehouses
            const warehousesSheet = workbook.Sheets['Склады'];
            const warehousesData = XLSX.utils.sheet_to_json(warehousesSheet);
            this.warehouses = warehousesData.map(row => new Warehouse(
                row['ID'],
                row['Название'],
                row['Адрес'],
                JSON.parse(row['Доп. информация'] || '{}')
            ));
            
            // Load inventory
            const inventorySheet = workbook.Sheets['Товары на складах'];
            const inventoryData = XLSX.utils.sheet_to_json(inventorySheet);
            this.inventory = inventoryData.map(row => new InventoryItem(
                row['Склад ID'],
                String(row['SKU товара']),
                parseInt(row['Количество'])
            ));
            
            // Load destinations
            const destinationsSheet = workbook.Sheets['ПП'];
            const destinationsData = XLSX.utils.sheet_to_json(destinationsSheet);
            this.destinations = destinationsData.map(row => new Destination(
                row['ID'],
                row['Название'],
                row['Адрес'],
                String(row['SKU товара']),
                parseFloat(row['Требуемое кол-во'])
            ));
            
            // Load transports
            const transportSheet = workbook.Sheets['ТС'];
            const transportData = XLSX.utils.sheet_to_json(transportSheet);
            this.transports = transportData.map(row => new Transport(
                row['ID'],
                row['Название'],
                parseFloat(row['Грузоподъемность (кг)']),
                parseFloat(row['Расход топлива (л/100км)'])
            ));
            
            // Populate warehouse cargos
            this._populateWarehouseCargos();
            
            // Validate data
            if (!this.validateData()) {
                throw new Error('Invalid data in Excel file');
            }
            
            // Convert to your existing dbData format
            const dbData = {
                cargoTypes: this.products.map(p => ({
                    name: p.name,
                    weight: p.weight,
                    sku: p.sku,
                    features: p.features
                })),
                truckTypes: this.transports.map(t => ({
                    name: t.name,
                    capacity: t.maxLoad,
                    fuel: t.fuelConsumption
                })),
                warehouses: this.warehouses.map(w => ({
                    name: w.name,
                    address: w.address,
                    cargos: w.cargos.map(c => ({
                        type: this.getProductBySku(c.productSku)?.name || c.productSku,
                        quantity: c.quantity
                    }))
                })),
                destinations: this.destinations.map(d => ({
                    name: d.name,
                    address: d.address,
                    cargos: [{
                        type: this.getProductBySku(d.productSku)?.name || d.productSku,
                        quantity: d.requiredQuantity
                    }]
                }))
            };
            
            // Update UI lists
            updateCargoTypesList();
            updateTruckTypesList();
            updateWarehousesList();
            updateDestinationsList();
            
            statusElement.textContent = 'Данные успешно загружены из Excel';
            statusElement.style.color = 'green';
            
            return dbData;
            
        } catch (error) {
            console.error('Ошибка загрузки Excel:', error);
            statusElement.textContent = 'Ошибка загрузки Excel';
            statusElement.style.color = 'red';
            alert(`Ошибка загрузки Excel: ${error.message}`);
            throw error;
        }
    }
    
    _populateWarehouseCargos() {
        // Group inventory by warehouse
        const inventoryByWarehouse = {};
        this.inventory.forEach(item => {
            if (!inventoryByWarehouse[item.warehouseId]) {
                inventoryByWarehouse[item.warehouseId] = [];
            }
            inventoryByWarehouse[item.warehouseId].push(item);
        });
        
        // Populate cargos for each warehouse
        this.warehouses.forEach(warehouse => {
            const items = inventoryByWarehouse[warehouse.id] || [];
            warehouse.cargos = items.map(item => ({
                productSku: item.productSku,
                quantity: item.quantity
            }));
        });
    }
    
    getWarehouseById(warehouseId) {
        return this.warehouses.find(w => w.id === warehouseId);
    }
    
    getProductBySku(sku) {
        return this.products.find(p => p.sku === sku);
    }
    
    getInventoryForWarehouse(warehouseId) {
        return this.inventory.filter(item => item.warehouseId === warehouseId);
    }
    
    getDestinationsForProduct(productSku) {
        return this.destinations.filter(d => d.productSku === productSku);
    }
    
    validateData() {
        // Check inventory references
        for (const item of this.inventory) {
            if (!this.getWarehouseById(item.warehouseId)) {
                console.error(`Ошибка: склад ${item.warehouseId} не найден для товара ${item.productSku}`);
                return false;
            }
            
            if (!this.getProductBySku(item.productSku)) {
                console.error(`Ошибка: товар ${item.productSku} не найден на складе ${item.warehouseId}`);
                return false;
            }
        }
        
        // Check destination references
        for (const dest of this.destinations) {
            if (!this.getProductBySku(dest.productSku)) {
                console.error(`Ошибка: товар ${dest.productSku} не найден для пункта назначения ${dest.name}`);
                return false;
            }
        }
        
        return true;
    }
}

// Global instance
const transportData = new TransportTaskData();

// File input handler
document.getElementById('excel-file-input').addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
        const dbData = await transportData.loadFromExcel(file);
        // Save to cookies if needed
        Cookies.set('dbData', JSON.stringify(dbData), { expires: 1 });
    } catch (error) {
        console.error('Error processing Excel file:', error);
    }
});