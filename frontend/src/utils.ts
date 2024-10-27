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

export default {
  sleep,
  getUSBFromDevice,
  getThumbnailFromProduct,
}
