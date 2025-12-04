lines = readlines("input.txt");
H = numel(lines);
W = strlength(lines(1));
G = char(lines); 
M = (G == '@');  
K = ones(3); 
neighbor_counts = conv2(double(M), K, 'same') - M;
accessible_mask = M & (neighbor_counts < 4);
answer = nnz(accessible_mask);
