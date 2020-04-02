#!/bin/bash
paste <(awk "{print \"$1/\"}" <$2) $2 | tr -d '\t' > $3