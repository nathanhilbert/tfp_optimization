#!/usr/bin/python

import random
import sys


def rand_seq(size):
    '''generates values in random order
    equivalent to using shuffle in random,
    without generating all values at once'''
    values=range(size)
    for i in xrange(size):
        # pick a random index into remaining values
        j=i+int(random.random()*(size-i))
        # swap the values
        values[j],values[i]=values[i],values[j]
        # return the swapped value
        yield values[i] 

def all_pairs(size):
    '''generates all i,j pairs for i,j from 0-size'''
    for i in rand_seq(size):
        for j in rand_seq(size):
            yield (i,j)

def reversed_sections(tour):
    '''generator to return all possible variations where the section between two cities are swapped'''
    for i,j in all_pairs(len(tour)):
        if i != j:
            copy=tour[:]
            if i < j:
                copy[i:j+1]=reversed(tour[i:j+1])
            else:
                copy[i+1:]=reversed(tour[:j])
                copy[:j]=reversed(tour[i+1:])
            if copy != tour: # no point returning the same tour
                yield copy


#
#def init_matrix():    
#    '''create a distance matrix for the city coords that uses straight line distance'''
#    matrix={}
#    matrix[2,9] =    110
#    matrix[2,7] =  62
#    matrix[2,6] =  58
#    matrix[2,5] =  90
#    matrix[5,9] =  57
#    matrix[5,7] =  151
#    matrix[5,6] =  104
#    matrix[5,2] =  90
#    matrix[6,9] =  147
#    matrix[6,7] =  74
#    matrix[6,5] =  104
#    matrix[6,2] =  58
#    matrix[7,9] =  172
#    matrix[7,6] =  74
#    matrix[7,5] =  151
#    matrix[7,2] =  62
#    matrix[9,7] =    172
#    matrix[9,6] =  147
#    matrix[9,5] =  57
#    matrix[9,2] =  110
#    return matrix



def tour_length(matrix,tour):
    '''total up the total length of the tour based on the distance matrix'''
    
    total=0
    num_cities=len(tour)
    for i in range(num_cities):
        j=(i+1)%num_cities
        city_i=tour[i]
        city_j=tour[j]
        total+=matrix[city_i,city_j]
    return total


def init_random_tour(storelist):
   return storelist

def run_hillclimb(init_function,move_operator,objective_function,max_iterations):
    from hillclimb import hillclimb_and_restart
    iterations,score,best=hillclimb_and_restart(init_function,move_operator,objective_function,max_iterations)
    return iterations,score,best


def usage():
    print "usage: python %s [-o <output image file>] [-v] [-m reversed_sections|swapped_cities] -n <max iterations> [-a hillclimb|anneal] [--cooling start_temp:alpha] <city file>" % sys.argv[0]



def tspfunction(matrix, storelist, DEBUG):
    
    #make market sets coordinates


    max_iterations=1000
    verbose=False
    move_operator=reversed_sections
    run_algorithm=run_hillclimb
    
    # enable more verbose logging (if required) so we can see workings
    # of the algorithms
    import logging
    format='%(asctime)s %(levelname)s %(message)s'
    if verbose:
        logging.basicConfig(level=logging.INFO,format=format)
    else:
        logging.basicConfig(format=format)
    
    # setup the things tsp specific parts hillclimb needs

    
    
    init_function=lambda: init_random_tour(storelist)
    
    objective_function=lambda tour: -tour_length(matrix,tour)
    
    logging.info('using move_operator: %s'%move_operator)
    
    iterations,score,best=run_algorithm(init_function,move_operator,objective_function,max_iterations)
    # output results
    #print "here it is",iterations,score,best
    return best


