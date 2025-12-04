lines = readlines("input.txt");
H = numel(lines);
W = strlength(lines(1));
G = char(lines); 
M = (G == '@');
K = ones(3); 
neighbor_counts = conv2(double(M), K, 'same') - double(M);
accessible_mask = M & (neighbor_counts < 4);
answer1 = nnz(accessible_mask);

M2 = M;
total_removed = 0;
while true
    neighbor_counts2 = conv2(double(M2), K, 'same') - double(M2);
    accessible_now = M2 & (neighbor_counts2 < 4);
    removed_this_round = nnz(accessible_now);
    if removed_this_round == 0
        break;
    end
    M2(accessible_now) = false;
    total_removed = total_removed + removed_this_round;
end
answer2 = total_removed
