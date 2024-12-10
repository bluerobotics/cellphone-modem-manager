/**
 * Sleep for a given amount of time
 * @param {number} ms The amount of time to sleep in milliseconds
 * @returns {Promise<void>}
 */
export const sleep = (ms: number): Promise<void> => new Promise(resolve => setTimeout(resolve, ms))

/**
 * Extracts USB name from device path
 * @param {string} device The device path to be used to search for the USB name
 * @returns {string} The USB name extracted from the device path if found, otherwise "UNKNOWN"
 */
export const getUSBFromDevice = (device: string): string => {
  const match = RegExp(/\/(usb\d+)/).exec(device);

  return match ? match[1].toUpperCase() : "UNKNOWN";
};

/**
 * Gets a thumbnail image path from a product name
 * @param product The product name to be used to search for the thumbnail
 * @returns {string} The thumbnail image path
 */
export const getThumbnailFromProduct = (product: string): string => `/static/thumbs/${product.toLowerCase()}.png`;

/**
 * Gets the base ApexChart options for modem extension
 * @param {string} title The title of the chart
 * @param {string} xTitle The title of the x-axis
 * @param {string} yTitle The title of the y-axis
 * @returns {Record<string, any>} The base ApexChart options
 */
export const getBaseApexChartOptions = (
  title?: string,
  xTitle?: string,
  yTitle?: string,
  yMin?: number,
  yMax?: number
): Record<string, any> => {
  return {
    chart: {
      toolbar: { show: false },
      foreColor: 'white'
    },
    tooltip: { enabled: false },
    dataLabels: { enabled: false },
    title: {
      text: title,
      align: 'center',
      style: {
        fontSize: '16px',
        color: 'white'
      }
    },
    yaxis: {
      title: {
        text: yTitle,
        style: {
          fontSize: '14px',
          color: 'white'
        }
      },
      labels: {
        style: {
          colors: 'white'
        }
      },
      min: yMin,
      max: yMax
    },
    xaxis: {
      title: {
        text: xTitle,
        style: {
          fontSize: '14px',
          color: 'white'
        }
      },
      labels: {
        show: true,
        style: {
          colors: 'white'
        }
      }
    },
    grid: {
      borderColor: 'white',
    }
  };
}

export default {
  sleep,
  getUSBFromDevice,
  getThumbnailFromProduct,
  getBaseApexChartOptions,
}
