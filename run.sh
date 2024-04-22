#!/bin/bash

usage() {
  echo "Usage: $0 [--apply] [--destroy]" 1>&2
  exit 1
}

# create virtual environment
activating_venv() {
  source .venv/bin/activate
  export PYTHONPATH=$PWD
}


main() {

  if [[ "$VIRTUAL_ENV" == "" ]]
  then
    echo "No virtual environment is there."
    echo "Activating New virtual environment ... .. ."
    activating_venv
  else
    echo "Virtual Environment is already activated"
  fi

  case $1 in
    --apply)
      python3 dexpo/main.py --apply ;;

    --destroy)
      python3 dexpo/main.py --destroy ;;

    *)
      usage

  esac

}

# Entrypoint
main $1
