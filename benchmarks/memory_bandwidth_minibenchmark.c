
#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <sched.h>
#include <string.h>

typedef struct {
    int squere_length;
    cpu_set_t mask;
} thread_struct;

#define MAX_TASKS (21)
#define THREAD_NAME "mem_band_**"

void *myThreadFun(void *vargp)
{
    int length = 0;
    int i = 0, j = 0;
    volatile int **mat;
    volatile int sum = 0;
    volatile int true_var = 1;

    thread_struct * ptr = (thread_struct *)vargp;
    length = ptr->squere_length;

    sched_setaffinity(0, sizeof(ptr->mask), &ptr->mask);

    if (( mat = malloc( length * sizeof( int* ))) == NULL )
        { exit(0); }

    for ( i = 0; i < length; i++ )
    {
        if (( mat[i] = malloc( length * sizeof(int) )) == NULL )
        { exit(0); }
    }

    while(true_var)
    {
        for(i = 0; i < length; i++)
        {
            for(j = 0; j < length; j++)
            {
                sum += mat[j][i];
            }
        }
    }
    return NULL;
}

int main(int argc, char *argv[])
{
    int number_of_tasks, length, i;
    int **mat;
    int core_index;
    pthread_t threads[MAX_TASKS];
    thread_struct tss[MAX_TASKS];
    char thread_name [20];

    if ( argc != 3 ) /* local cycles each iteration, first CPU id and second */
    {
        printf( "usage: %s filename number of tasks, squere size \n", argv[0] );
        exit(0);
    }

    number_of_tasks = atoi(argv[1]);
    if ( number_of_tasks > 22 ) /* more than existing physical cores in one socket */
    {
        printf( "Number of tasks requested too big\n");
        exit(0);
    }

    length = atoi(argv[2]);

    strcpy(thread_name, THREAD_NAME);

    for(i = 0; i < number_of_tasks; i++)
    {
        printf("i = %d\n", i);
        tss[i].squere_length = length;
        core_index = 3 + (2 * i);
        CPU_ZERO(&tss[i].mask);
        CPU_SET(core_index, &tss[i].mask);
        pthread_create(&threads[i], NULL, myThreadFun, &tss[i]);
        thread_name[10] = (core_index % 10) + '0';
        thread_name[9] = (core_index / 10) + '0';
        pthread_setname_np(threads[i], thread_name);
    }    

    for(i = 0; i < number_of_tasks; i++)
    {
        pthread_join(threads[i], NULL);
    }


    free(mat);
    exit(0);
}
