<template>
  <div class="map-container" ref="mapContainer"></div>
</template>

<script setup lang="ts">
import { Ref, ref, watch, defineProps } from 'vue';
import { ModemDevice, ModemCellInfo, CellLocation } from '@/types/ModemManager';
import ModemManager from '@/services/ModemManager';
import mapboxgl from 'mapbox-gl';

const props = defineProps<{
  modem: ModemDevice;
  cellInfo: ModemCellInfo | null;
}>();

/** States */
const mapContainer = ref<HTMLElement | null>(null);
const servingCellLocation = ref<CellLocation | null>(null);
const map = ref<mapboxgl.Map | null>(null) as Ref<mapboxgl.Map | null>;

/** Utils */

const createMap = () => {
  mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_GL_ACCESS_TOKEN;

  const temp = new mapboxgl.Map({
    container: mapContainer.value!,
    style: 'mapbox://styles/mapbox/streets-v11',
    center: [0, 0],
    zoom: 1,
  });
  temp.addControl(new mapboxgl.NavigationControl());

  map.value = temp;
};

/** Watchers */
watch(mapContainer, (newContainer) => {
  if (newContainer) {
    createMap();
  }
});

watch(() => props.cellInfo, async (newCellInfo) => {
  try {
    if (!newCellInfo || !newCellInfo?.serving_cell) {
      return;
    }

    console.log('Fetching cell location', newCellInfo.serving_cell);

    servingCellLocation.value = await ModemManager.fetchCellCoordinates(
      newCellInfo?.serving_cell.mobile_country_code,
      newCellInfo?.serving_cell.mobile_network_code,
      newCellInfo?.serving_cell.area_id,
      newCellInfo?.serving_cell.cell_id,
    )
  } catch (error) {
    console.error("Unable to locate cell tower", error);
  }
});

watch(servingCellLocation, (newLocation) => {
  if (!newLocation) {
    return;
  }

  console.log('Setting map center', newLocation);

  map.value?.setCenter([newLocation.longitude, newLocation.latitude]);
  // Add a marker to the map
  new mapboxgl.Marker()
    .setLngLat([newLocation.longitude, newLocation.latitude])
    .addTo(map.value!);
});
</script>

<style scoped>
.map-container {
  flex: 1;
  flex-grow: 1;
  width: 100%;
  padding: 16px;
  height: 378px;
}
</style>
