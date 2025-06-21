async function buildRoutes() {
    try {
        const response = await fetch('/api/logistics');
        const data = await response.json();
        const warehouses = data.warehouses;
        const destinations = data.destinations;

        const routesData = [];

        for (const warehouse of warehouses) {
            const fromGeo = await ymaps.geocode(warehouse.address);
            const fromGeoObject = fromGeo.geoObjects.get(0);

            if (!fromGeoObject) {
                console.warn(`Адрес склада не найден: ${warehouse.address}, пропускаем...`);
                continue;
            }
            const fromCoords = fromGeoObject.geometry.getCoordinates();

            for (const dest of destinations) {
                const toGeo = await ymaps.geocode(dest.address);
                const toGeoObject = toGeo.geoObjects.get(0);

                if (!toGeoObject) {
                    console.warn(`Адрес пункта приёма не найден: ${dest.address}, пропускаем...`);
                    continue;
                }
                const toCoords = toGeoObject.geometry.getCoordinates();

                try {
                    const route = await ymaps.route([fromCoords, toCoords]);
                    const pathCoords = route.getPaths().get(0).geometry.getCoordinates();
                    const distance = route.getLength();
                    const duration = route.getTime();

                    routesData.push({
                        from: warehouse.name,
                        to: dest.name,
                        from_address: warehouse.address,
                        to_address: dest.address,
                        distance_m: distance,
                        duration_min: Math.round(duration / 60000),
                        path: pathCoords
                    });
                } catch (error) {
                    console.error(`Ошибка при построении маршрута от ${warehouse.name} до ${dest.name}:`, error);
                }
            }
        }

        const resp = await fetch('/api/compute-routes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json; charset=utf-8' },
            body: JSON.stringify(routesData)
        });

        const result = await resp.json();
        console.log("Маршруты успешно рассчитаны:", result);

        if (result.success) {
            window.dispatchEvent(new CustomEvent('routesUpdated', { detail: result }));
        }

        await fetch('/api/save-routes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify()
        });

        console.log("Маршруты успешно отправлены на сервер.");
    } catch (error) {
        console.error('Ошибка при построении маршрутов:', error);
    }
}

// Вызываем функцию сразу после загрузки
if (typeof ymaps !== 'undefined' && ymaps.ready) {
    ymaps.ready(buildRoutes);
}