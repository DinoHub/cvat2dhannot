#!/bin/bash
paste <(awk "{print \"$PWD/\"}" <$1) $1 | tr -d '\t' > $2