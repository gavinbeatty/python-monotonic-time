#include <sys/time.h>

#include <mach/clock.h>
#include <mach/clock_types.h>
#include <mach/mach_host.h>
#include <mach/clock.h>

int darwin_clock_gettime_MONOTONIC(struct timespec *tp)
{
    mach_timespec_t mach_tp;
    clock_serv_t clock_ref;
    kern_return_t ret = host_get_clock_service(mach_host_self(), SYSTEM_CLOCK, &clock_ref);
    if (ret != KERN_SUCCESS) {
        /* XXX errno already set or should we set it? */
        return -1;
    }
    ret = clock_get_time(clock_ref, &mach_tp);
    if (ret != KERN_SUCCESS) {
        /* XXX errno already set or should we set it? */
        return -1;
    }
    tp->tv_sec = mach_tp.tv_sec;
    tp->tv_nsec = mach_tp.tv_nsec;
    return 0;
}

