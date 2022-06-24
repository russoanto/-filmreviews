#!/bin/bash

cd filmreviews
echo ""
echo "-----------------------------------------------------------------------"

while [ "$order" != "n" ]
do
    echo 'Eseguo il main: --> esempio query (title:Joker AND content:C*)'
    echo ""
    python main.py
    echo "vuoi fare un'altra query? (default - invio 'continue', altrimenti n per andare al benchmark): "
    read order
done

echo "-----------------------------------------------------------------------"
echo "Fine query"
echo ""
echo "-----------------------------------------------------------------------"
echo 'Eseguo il benchmark:'
echo ""
python main.py benchmark query_benchmark
echo "-----------------------------------------------------------------------"
echo "Finito l'esecuzione"
echo ""
echo "-----------------------------------------------------------------------"
