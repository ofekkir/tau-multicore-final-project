#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <sched.h>

typedef struct {
    int local_cycles;
    cpu_set_t mask;
} thread_struct;

int shared_var = 0;

void *myThreadFun(void *vargp)
{
    int local_var = 0;
    int i = 0;

    thread_struct * ptr = (thread_struct *)vargp;
    int local_cycles = ptr->local_cycles;

    sched_setaffinity(0, sizeof(ptr->mask), &ptr->mask);

    while(1)
    {
        for(i = 0; i < local_cycles; i++)
        {
            local_var++;
        }
        shared_var++;
//      printf("shared_var %d \n", shared_var);

    }
    return NULL;
}

int main()
{
    pthread_t t1, t2;
    thread_struct ts1, ts2;
    ts1.local_cycles = 1000;
    ts2.local_cycles = 1000;
    CPU_ZERO(&ts1.mask);
    CPU_ZERO(&ts2.mask);

    CPU_SET(0, &ts1.mask);
    CPU_SET(0, &ts2.mask);

    pthread_create(&t1, NULL, myThreadFun, &ts1);
    pthread_create(&t2, NULL, myThreadFun, &ts2);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    exit(0);
}

    pthread_create(&t1, NULL, myThreadFun, &ts1);
    pthread_create(&t2, NULL, myThreadFun, &ts2);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    exit(0);
}
