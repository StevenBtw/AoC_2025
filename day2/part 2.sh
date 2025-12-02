invalid_total=0

input=$(cat input.txt)
input=$(echo "$input" | tr -d ' \n')
input=${input%,}

IFS=',' read -ra id_ranges <<< "$input"

for id_range in "${id_ranges[@]}"; do

    IFS='-' read -r start_id end_id <<< "$id_range"

    for ((id = start_id; id <= end_id; id++)); do

        id_string="$id"
        length=${#id_string}
        is_invalid=false

        for ((part_length = 1; part_length <= length / 2; part_length++)); do

            if (( length % part_length != 0 )); then
                continue
            fi

            part=${id_string:0:part_length}
            repeat_count=$(( length / part_length ))

            repeated=""
            for ((r = 0; r < repeat_count; r++)); do
                repeated="${repeated}${part}"
            done

            if [[ "$repeated" == "$id_string" ]]; then
                is_invalid=true
                break
            fi

        done

        if [[ "$is_invalid" == true ]]; then
            invalid_total=$(( invalid_total + id ))
        fi

    done
done

echo "$invalid_total"
