#!/bin/bash
for i in `ls ~/zstack-woodpecker/integrationtest/vm/${1} | grep ^test.*py$`
do
    ln -s ../../${1}${i}
done

