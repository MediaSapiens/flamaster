#!/usr/bin/env bash

COFFEE=`which coffee`
${COFFEE} -b -w -o flamaster/static/js/ front/
