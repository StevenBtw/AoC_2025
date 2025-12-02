input=$(cat input.txt)
input=$(echo "$input" | tr -d ' ')

IFS=',' read -ra id_ranges <<< "$input"

for id_range in "${id_ranges[@]}"; do

    IFS='-' read -r start_id end_id <<< "$id_range"

    for ((id = start_id; id <= end_id; id++)); do

        id_string="$id"
        length=${#id_string}

        if (( length % 2 != 0 )); then
            continue
        fi

        half=$(( length / 2 ))

        first_half=${id_string:0:half}
        second_half=${id_string:half}

        if [[ "$first_half" == "$second_half" ]]; then
            invalid_total=$(( invalid_total + id ))
        fi

    done
done

echo "$invalid_total"
