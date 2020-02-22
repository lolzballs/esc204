#ifndef STEPPERD_STEPPERD_H
#define STEPPERD_STEPPERD_H

#include "commands.h"
#include "event.h"

#include <gpiod.h>
#include <stdbool.h>
#include <time.h>

struct stepperd_target {
    bool is_valid;
    bool clockwise;
    uint32_t step_count;
    uint32_t steps_elapsed;
};

struct stepperd_motor {
    struct gpiod_line *step_pin;
    struct gpiod_line *dir_pin;
    uint32_t steps_per_rot; // steps per 360 degrees
    uint32_t cur_step; // current steps

    struct stepperd_target target;
};

struct stepperd {
    struct rio rio;
    struct commands commands;

    bool pending;
    uint32_t step_time; // T_high, T_low in ns
    struct gpiod_chip *chip;
    struct stepperd_motor motors[2];
};

#endif

