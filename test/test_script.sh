#!/bin/bash

tagfs
tagfs init
tagfs addtags topics eresources
tagfs addtags mathematics physics computerscience 
tagfs addtags calculus quantumphysics quantumcomputing
tagfs addtags books articles researchpapers

tagfs linktags books eresources
tagfs linktags articles eresources
tagfs linktags researchpapers eresources

tagfs linktags mathematics topics
tagfs linktags physics topics
tagfs linktags computerscience topics
tagfs linktags calculus mathematics
tagfs linktags quantumphysics physics
tagfs linktags quantumcomputing computerscience
tagfs linktags quantumcomputing quantumphysics

tagfs addresource dir1/calculus.txt
tagfs addresource dir1/math.txt
tagfs addresource dir2/physics.txt
tagfs addresource dir2/quantummechanics.txt

tagfs tagresource dir1/calculus.txt calculus
tagfs tagresource dir1/math.txt mathematics
tagfs tagresource dir2/physics.txt physics
tagfs tagresource dir2/quantummechanics.txt quantumphysics


