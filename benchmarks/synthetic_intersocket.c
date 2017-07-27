#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <sched.h>
#include <string.h>

typedef struct {
    int local_cycles;
    cpu_set_t mask;
    int * shared_arr;
    int num;
} thread_struct;

int shared_arr1[10];
int shared_arr2[10];

void *myThreadFun(void *vargp)
{
    int local_var = 0;
    int i = 0;
    int j = 0;

    thread_struct * ptr = (thread_struct *)vargp;
    int local_cycles = ptr->local_cycles;

    j = ptr->num % 10;
    sched_setaffinity(0, sizeof(ptr->mask), &ptr->mask);

    while(1)
    {
        for(i = 0; i < local_cycles; i++)
        {
            local_var++;
        }
        (ptr->shared_arr[j])++;
        j = (j + 1) % 10;
    }
    return NULL;
}

int main(int argc, char *argv[])
{
    int group_size, local_cycles, core1, core2;
    int i = 0;
    int core_index = 2;
    pthread_t threads[60];
    thread_struct tss [60];

    if ( argc != 3 ) /* local cycles each iteration, first CPU id and second */
    {
        printf( "argc = %d\n", argc );
        exit(0);
    }

    local_cycles = atoi(argv[1]);
    group_size = atoi(argv[2]);

    for(i = 0; i < group_size; i++)
    {
        tss[i].local_cycles = local_cycles;
        tss[i].shared_arr = &shared_arr1[0];
        tss[i + group_size].local_cycles = local_cycles;
        tss[i + group_size].shared_arr = &shared_arr2[0];

        core_index = 2 + i;
        tss[i].num = core_index;
        CPU_ZERO(&tss[i].mask);
        CPU_SET(core_index, &tss[i].mask);
        pthread_create(&threads[i], NULL, myThreadFun, &tss[i]);
        pthread_setname_np(threads[i], "group_A");
        printf("thread %d created \n", core_index);
        core_index = 2 + group_size + i;
        tss[i + group_size].num = core_index;
        CPU_ZERO(&tss[i + group_size].mask);
        CPU_SET(core_index, &tss[i + group_size].mask);
        pthread_create(&threads[i + group_size], NULL, myThreadFun, &tss[i + group_size]);
        pthread_setname_np(threads[i + group_size], "group_B");
        printf("thread %d created \n", core_index);
    }

    for(i = 0; i < 60; i++)
    {
        pthread_join(threads[i], NULL);
    }

    exit(0);
}
