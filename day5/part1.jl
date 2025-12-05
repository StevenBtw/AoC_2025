function split_input(path::AbstractString)
    lines = readlines(path)
    clean = filter(s -> !isempty(strip(s)), lines)
    isrange(s) = occursin('-', s)
    range_lines  = filter(isrange, clean)
    number_lines = filter(s -> !isrange(s), clean)

    return range_lines, number_lines
end

function merge_ranges(ranges::Vector{Tuple{Int,Int}})
    sort!(ranges, by = x -> x[1])
    merged = Vector{Tuple{Int,Int}}()
    current = ranges[1]

    for r in ranges[2:end]
        if r[1] <= current[2]
            current = (current[1], max(current[2], r[2]))
        else
            push!(merged, current)
            current = r
        end
    end

    push!(merged, current)
    return merged
end

function count_not_in_ranges(numbers::Vector{Int}, merged::Vector{Tuple{Int,Int}})
    count = 0

    for n in numbers
        inside = false
        for (a,b) in merged
            if a <= n <= b
                inside = true
                break
            end
        end
        if !inside
            count += 1
        end
    end

    return count
end

range_lines, number_lines = split_input("input.txt")
ranges = [begin
    a, b = split(strip(s), '-')
   (parse(Int, a), parse(Int, b)) 
end for s in range_lines]

numbers = parse.(Int, strip.(number_lines))
merged = merge_ranges(ranges)
missing_count = count_not_in_ranges(numbers, merged)
fresh_count = length(numbers) - missing_count
println(fresh_count)

