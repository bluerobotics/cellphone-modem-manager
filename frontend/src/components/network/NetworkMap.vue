<template>
  <div v-if="servingLocation !== null || vehicleLocation !== null" class="map-container" ref="mapContainer"></div>
  <div v-else class="no-info-available">
    <strong>No nearby cells info available. Unable to render Map.</strong>
  </div>
</template>

<script setup lang="ts">
import mapboxgl from 'mapbox-gl';

import { Ref, ref, watch, defineProps, computed } from 'vue';

import { OneMoreTime } from '@/one-more-time';
import ModemManager from '@/services/ModemManager';
import { ModemDevice, ModemCellInfo, CellLocation, ModemPosition, NearbyCellTower } from '@/types/ModemManager';

/** Props / Emits */
const props = defineProps<{
  modem: ModemDevice;
  cellInfo: ModemCellInfo | null;
}>();

/** States */
const mapContainer = ref<HTMLElement | null>(null);
const map = ref<mapboxgl.Map | null>(null) as Ref<mapboxgl.Map | null>;

const servingLocation = ref<CellLocation | null>(null);
const vehicleLocation = ref<ModemPosition | null>(null);
const neighborLocation = ref<NearbyCellTower[]>([]);

/** Computed */
const mapCenter = computed<[number, number]>(() => {
  if (vehicleLocation.value !== null) {
    return [vehicleLocation.value.longitude, vehicleLocation.value.latitude];
  }

  if (servingLocation.value !== null) {
    return [servingLocation.value.longitude, servingLocation.value.latitude];
  }

  return [0, 0];
});

/** Utils */
const createMapLayer = (name: string, source: string, layer: string, img: string, size: number = 0.7) => {
  if (!map.value) {
    return;
  }

  const onImgLoad = (error: any, image: any) => {
    if (error) return;

    if (!map.value?.hasImage(name)) {
      map.value?.addImage(name, image);
    }

    map.value?.addSource(
      source,
      {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: []
        }
      }
    );

    map.value?.addLayer(
      {
        id: layer,
        type: 'symbol',
        source: source,
        layout: {
          'icon-image': name,
          'icon-size': size
        }
      }
    );
  }

  map.value.loadImage(img, onImgLoad);
}

const initLayers = () => {
  createMapLayer('serving-cell', 'serving-cell-source', 'serving-cell-layer', '/static/radio/serving.png');
  createMapLayer('vehicle', 'vehicle-source', 'vehicle-layer', '/static/radio/vehicle.png');
  createMapLayer('2g-neighbor', '2g-neighbor-source', '2g-neighbor-layer', '/static/radio/2g.png');
  createMapLayer('3g-neighbor', '3g-neighbor-source', '3g-neighbor-layer', '/static/radio/3g.png');
  createMapLayer('4g-neighbor', '4g-neighbor-source', '4g-neighbor-layer', '/static/radio/4g.png');
}

const createMap = () => {
  mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_GL_ACCESS_TOKEN;

  const temp = new mapboxgl.Map({
    container: mapContainer.value!,
    style: 'mapbox://styles/mapbox/streets-v11',
    center: mapCenter.value,
    zoom: 1,
  });
  temp.addControl(new mapboxgl.NavigationControl());

  map.value = temp;
  map.value?.setZoom(15);

  initLayers();
};

const fetchVehicleLocation = async () => {
  try {
    vehicleLocation.value = await ModemManager.fetchPositionById(props.modem.id);
  } catch (error) {
    vehicleLocation.value = null;
    console.error('Failed to fetch Vehicle Position, error:', (error as any)?.message);
  }
}

/** Watchers */
watch(mapContainer, (newContainer) => {
  if (newContainer && !map.value) {
    createMap();
  }
});

watch(() => props.cellInfo, async (newCellInfo) => {
  try {
    if (!newCellInfo || !newCellInfo?.serving_cell) {
      return;
    }

    servingLocation.value = await ModemManager.fetchCellCoordinates(
      newCellInfo?.serving_cell.mobile_country_code,
      newCellInfo?.serving_cell.mobile_network_code,
      newCellInfo?.serving_cell.area_id,
      newCellInfo?.serving_cell.cell_id,
    )

    neighborLocation.value = await ModemManager.fetchNearbyCellsCoordinates(
      servingLocation.value.latitude,
      servingLocation.value.longitude
    );
  } catch (error) {
    servingLocation.value = null;
    neighborLocation.value = [];

    console.error('Failed to fetch Serving Cell Location, error:', (error as any)?.message);
  }
});

watch(servingLocation, (newLocation) => {
  if (!newLocation || !map.value) {
    return;
  }

  // We only center on the serving cell location if the vehicle location is not available
  if (vehicleLocation === null) {
    map.value?.setCenter([newLocation.longitude, newLocation.latitude]);
  }

  const source = map.value?.getSource('serving-cell-source') as mapboxgl.GeoJSONSource;

  if (!source) {
    return;
  }

  source.setData({
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [newLocation.longitude, newLocation.latitude]
        },
        properties: {
          title: 'Serving Cell',
          description: 'Serving Cell Location'
        }
      }
    ]
  });
});

watch(vehicleLocation, (newLocation) => {
  if (!newLocation || !map.value) {
    return;
  }

  map.value?.setCenter([newLocation.longitude, newLocation.latitude]);

  const source = map.value?.getSource('vehicle-source') as mapboxgl.GeoJSONSource;

  if (!source) {
    return;
  }

  source.setData({
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [newLocation.longitude, newLocation.latitude]
        },
        properties: {
          title: 'Vehicle',
          description: 'Vehicle Location'
        }
      }
    ]
  });
});

watch(neighborLocation, (newLocations) => {
  if (!newLocations || !map.value) {
    return;
  }

  const Source2G = map.value?.getSource('2g-neighbor-source') as mapboxgl.GeoJSONSource;
  const Source3G = map.value?.getSource('3g-neighbor-source') as mapboxgl.GeoJSONSource;
  const Source4G = map.value?.getSource('4g-neighbor-source') as mapboxgl.GeoJSONSource;

  if (!Source2G || !Source3G || !Source4G) {
    return;
  }

  const nearby2G = newLocations.filter((cell) => cell.radio.type.includes('GSM'));
  const nearby3G = newLocations.filter((cell) =>
    ['UMTS', 'HSPA', 'HSPA+', 'WCDMA'].some((type) => cell.radio.type.includes(type))
  );
  const nearby4G = newLocations.filter((cell) => cell.radio.type.includes('LTE'));

  Source2G.setData({
    type: 'FeatureCollection',
    features: nearby2G.map((cell) => ({
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [cell.longitude, cell.latitude]
      },
      properties: {
        title: '2G Neighbor',
        description: '2G Neighbor Location'
      }
    }))
  });

  Source3G.setData({
    type: 'FeatureCollection',
    features: nearby3G.map((cell) => ({
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [cell.longitude, cell.latitude]
      },
      properties: {
        title: '3G Neighbor',
        description: '3G Neighbor Location'
      }
    }))
  });

  Source4G.setData({
    type: 'FeatureCollection',
    features: nearby4G.map((cell) => ({
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [cell.longitude, cell.latitude]
      },
      properties: {
        title: '4G Neighbor',
        description: '4G Neighbor Location'
      }
    }))
  });
});

/** Tasks */
new OneMoreTime({ delay: 20000, disposeWith: this }, fetchVehicleLocation);
</script>

<style scoped>
.map-container {
  flex: 1;
  flex-grow: 1;
  width: 100%;
  padding: 16px;
  height: 378px;
}

.no-info-available {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 350px;
}
</style>
