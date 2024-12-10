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

/**
 * Converts bytes to a human-readable level
 * @param {number} bytes The bytes to be converted
 * @returns {[number, string]} The level and unit
 */
export const bytesToLevel = (bytes: number, unit?: string): [number, string] => {
  if (unit) {
    switch (unit) {
      case "B":
        return [bytes, "B"];
      case "KB":
        return [bytes / (2 ** 10), "KB"];
      case "MB":
        return [bytes / (2 ** 20), "MB"];
      case "GB":
        return [bytes / (2 ** 30), "GB"];
      default:
        return [bytes, "B"];
    }
  }

  if (bytes < 2 ** 10) {
    return [bytes, "B"];
  } else if (bytes < 2 ** 20) {
    return [bytes / (2 ** 10), "KB"];
  } else if (bytes < 2 ** 30) {
    return [bytes / (2 ** 20), "MB"];
  } else {
    return [bytes / (2 ** 30), "GB"];
  }
};

/**
 * Converts a level to bytes
 * @param {number} level The level to be converted
 * @param {string} unit The unit of the level
 * @returns {number} The bytes
 */
export const levelToBytes = (level: number, unit: string): number => {
  switch (unit) {
    case "B":
      return level;
    case "KB":
      return level * (2 ** 10);
    case "MB":
      return level * (2 ** 20);
    case "GB":
      return level * (2 ** 30);
    default:
      return 0;
  }
};

export default {
  sleep,
  getUSBFromDevice,
  getThumbnailFromProduct,
  getBaseApexChartOptions,
  bytesToLevel,
  levelToBytes
}
