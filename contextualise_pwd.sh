#!/bin/bash
paste <(awk "{print \"$PWD/images/\"}" <$1) $1 | tr -d '\t' > $2