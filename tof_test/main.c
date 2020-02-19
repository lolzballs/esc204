#include <assert.h>
#include <unistd.h>

#include <gpiod.h>
#include <vl53l0x_api.h>
#include <vl53l0x_platform.h>

#define VERSION_REQUIRED_MAJOR 1
#define VERSION_REQUIRED_MINOR 0
#define VERSION_REQUIRED_BUILD 4823

#define L_XSHUT 17

void print_pal_error(VL53L0X_Error Status) {
    char buf[VL53L0X_MAX_STRING_LENGTH];
    VL53L0X_GetPalErrorString(Status, buf);
    printf("%i <-> %s\n", Status, buf);
}

int init_device(VL53L0X_Dev_t *dev, uint32_t addr, struct gpiod_line *xshut) {
    VL53L0X_Version_t version;
    VL53L0X_DeviceInfo_t device_info;
    int32_t ret;

    dev->I2cDevAddr = 0x29;
    dev->fd = VL53L0X_i2c_init("/dev/i2c-1", 0x29);
    if (dev->fd < 0) {
        fprintf(stderr, "failed to create i2c interface\n");
        return -1;
    }

    ret = VL53L0X_GetVersion(&version);
    if (ret != 0) {
        fprintf(stderr, "could not read version\n");
        return -1;
    }

    assert(version.major == VERSION_REQUIRED_MAJOR);
    assert(version.minor == VERSION_REQUIRED_MINOR);
    assert(version.revision == VERSION_REQUIRED_BUILD);

    if (addr == 0x29)
        goto done;

    assert(xshut != NULL);

    VL53L0X_Error status;

    assert(addr % 2 == 1);
    status = VL53L0X_SetDeviceAddress(dev, addr * 2);
    if (status != VL53L0X_ERROR_NONE) {
        fprintf(stderr, "failed to set address\n");
        return -1;
    }

    ret = close(dev->fd);
    if (ret != 0) {
        fprintf(stderr, "failed to close old i2c\n");
        return -1;
    }

    dev->I2cDevAddr = addr;
    dev->fd = VL53L0X_i2c_init("/dev/i2c-1", addr);
    if (dev->fd < 0) {
        fprintf(stderr, "failed to create new i2c interface\n");
        return -1;
    }

    ret = gpiod_line_set_value(xshut, 1);
    if (ret != 0) {
        fprintf(stderr, "failed to assert XSHUT\n");
        return -1;
    }

done:
    status = VL53L0X_DataInit(dev);
    if (status != VL53L0X_ERROR_NONE) {
        printf("VL53L0X_DataInit: ");
        print_pal_error(status);
        return -1;
    }

    status = VL53L0X_GetDeviceInfo(dev, &device_info);
    if (status != VL53L0X_ERROR_NONE) {
        printf("VL53L0X_DeviceInfo: ");
        print_pal_error(status);
        return -1;
    }

    printf("VL53L0X_GetDeviceInfo:\n");
    printf("Device Name : %s\n", device_info.Name);
    printf("Device Type : %s\n", device_info.Type);
    printf("Device ID : %s\n", device_info.ProductId);
    printf("ProductRevisionMajor : %d\n", device_info.ProductRevisionMajor);
    printf("ProductRevisionMinor : %d\n", device_info.ProductRevisionMinor);

    return 0;
}

int main() {
    VL53L0X_Dev_t dev_left, dev_right;
    struct gpiod_chip *gpio_chip;
    struct gpiod_line *xshut_line;
    int ret;

    gpio_chip = gpiod_chip_open_lookup("/dev/gpiochip0");
    if (gpio_chip == NULL) {
        fprintf(stderr, "failed to load gpio chip\n");
        return -1;
    }

    xshut_line = gpiod_chip_get_line(gpio_chip, L_XSHUT);
    if (xshut_line == NULL) {
        fprintf(stderr, "failed to get XSHUT line\n");
        return -1;
    }

    ret = gpiod_line_request_output(xshut_line, "ToF-XSHUT_L", 0);
    if (ret != 0) {
        perror("request_output XSHUT");
        return -1;
    }

    ret = init_device(&dev_right, 0x31, xshut_line);
    assert(ret == 0);
    ret = init_device(&dev_left, 0x29, NULL);
    assert(ret == 0);

    return 0;
}
