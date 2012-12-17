#!/bin/bash

# Continuous Integration script for SST
#
#  Options:
#    --bootstrap, --flake8, --unit, ---acceptance=BROWSER
#
#  Example:
#    bootstrap environment, run static checks, run unit tests, run
#    acceptance tests with default browser:
#
#    $ ./ci.sh --bootstrap --flake8 --unit --acceptance
#
#    * BROWSER options are "Firefox" and "Chrome".  Default is "Firefox".
#
#  Instructions:
#   1. ensure you have Xvfb, Firefox or Chrome/Chromium installed
#   2. $ bzr branch lp:selenium-simple-test
#   3. cd selenium-simple-test
#   4. run this this script
#


# command line options
while [ $# -gt 0 ]; do  # until you run out of parameters
    case "$1" in
        --bootstrap)
            BOOTSTRAP=1
            ;;
        --flake8)
            FLAKE8=1
            ;;
        --unit)
            UNIT=1
            ;;
        --acceptance)
            BROWSER="$2"
            if [[ "$BROWSER" == "Firefox" || "$BROWSER" == "Chrome" ]]; then
                shift
            elif [ -z "$BROWSER" ]; then
                BROWSER="Firefox"
            else
                echo "browser format $1 not recognized."
                echo "(try: --acceptance Firefox, or: $0 --acceptance Chrome)"
                exit
            fi
            ;;
    esac
    shift  # check next set of parameters
done

if [ -n "$BOOTSTRAP" ]; then
    echo "cleaning up..."
    rm -rf ENV results *.log *.xml
    echo "getting dependencies..."
    if [ -d sst-deps ]; then
        cd sst-deps
        bzr pull
        cd ..
    else
        bzr branch lp:~ubuntuone-hackers/selenium-simple-test/sst-deps
    fi
    echo "creating virtualenv..."
    virtualenv ENV
    source ENV/bin/activate
    echo "installing modules from dependencies branch..."
    pip install sst-deps/*.tar.gz
else
    source ENV/bin/activate
fi

echo "setting path..."
PATH=sst-deps:$PATH  # so bindings find chromedriver

if [ -n "$FLAKE8" ]; then
    echo "running flake8 (pyflakes/pep8) checks..."
    flake8 src/ docs/ sst-* *.py  > flake8.log
fi

echo "-----------------"
echo "environment info:"
echo "-----------------"

python -V
python -c "import django; print 'Django %s' % django.get_version()"
python -c "import selenium; print 'Selenium %s' % selenium.__version__"
./sst-run -V

# run unit tests
if [ -n "$UNIT" ]; then
     nosetests --with-xunit -e ENV -e testproject
fi

# run acceptance tests
if [ -n "$BROWSER" ]; then
    if [ "$BROWSER" == "Firefox" ]; then
        firefox -v
    fi
    ./sst-run --test -x -s -r xml -b $BROWSER --extended-tracebacks
fi

echo "done."