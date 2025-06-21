class TransportTaskData {
    constructor() {
        this.requiredSheets = ['Товары', 'Склады', 'Товары на складах', 'ПП', 'ТС'];
    }

    async loadFromExcel(file) {
        try {
            const data = await file.arrayBuffer();
            const workbook = XLSX.read(data);
            
            // Проверяем наличие всех необходимых листов
            this.requiredSheets.forEach(sheet => {
                if (!workbook.Sheets[sheet]) {
                    throw new Error(`Отсутствует обязательный лист: ${sheet}`);
                }
            });

            // Загрузка товаров
            const products = XLSX.utils.sheet_to_json(workbook.Sheets['Товары'])
                .map(p => ({
                    name: p['Название'],
                    weight: p['Вес (кг)'],
                    sku: String(p['SKU'])
                }));

            // Загрузка складов
            const warehouses = XLSX.utils.sheet_to_json(workbook.Sheets['Склады'])
                .map(w => ({
                    name: w['Название'],
                    address: w['Адрес'],
                    id: w['ID']
                }));

            // Загрузка инвентаря
            const inventory = XLSX.utils.sheet_to_json(workbook.Sheets['Товары на складах'])
                .map(i => ({
                    warehouseId: i['Склад ID'],
                    productSku: String(i['SKU товара']),
                    quantity: i['Количество']
                }));

            // Загрузка пунктов назначения
            const destinations = XLSX.utils.sheet_to_json(workbook.Sheets['ПП'])
                .map(d => ({
                    name: d['Название'],
                    address: d['Адрес'],
                    productSku: String(d['SKU товара']),
                    requiredQuantity: d['Требуемое кол-во']
                }));

            // Загрузка транспорта
            const transports = XLSX.utils.sheet_to_json(workbook.Sheets['ТС'])
                .map(t => ({
                    name: t['Название'],
                    capacity: t['Грузоподъемность (т)'],
                    fuel: t['Расход топлива (л/100км)']
                }));

            // Формируем данные для форм
            const dbData = {
                cargoTypes: products,
                truckTypes: transports,
                warehouses: warehouses.map(w => {
                    const warehouseCargos = inventory
                        .filter(i => i.warehouseId === w.id)
                        .map(i => {
                            const product = products.find(p => p.sku === i.productSku);
                            return {
                                type: product ? product.name : i.productSku,
                                quantity: i.quantity,
                                available: i.quantity
                            };
                        });
                    
                    return {
                        name: w.name,
                        address: w.address,
                        cargos: warehouseCargos
                    };
                }),
                destinations: destinations.map(d => {
                    const product = products.find(p => p.sku === d.productSku);
                    return {
                        name: d.name,
                        address: d.address,
                        cargos: [{
                            type: product ? product.name : d.productSku,
                            quantity: d.requiredQuantity
                        }]
                    };
                })
            };

            return dbData;
        } catch (error) {
            console.error('Ошибка обработки Excel:', error);
            throw error;
        }
    }
}

// Создаем глобальный экземпляр
const transportData = new TransportTaskData();