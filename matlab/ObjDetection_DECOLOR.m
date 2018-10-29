function [LowRank,Mask,tau,info] = ObjDetection_DECOLOR(ImData,opt)
% This function use DECOLOR to detect moving objects in sequence ImData
% http://arxiv.org/PS_cache/arxiv/pdf/1109/1109.0882v1.pdf
% eexwzhou@ust.hk 
% Syntex: [LowRank,Mask,tau] = ObjDetection_DECOLOR(ImData).
% Input:
%   ImData -- 3D array representing a image sequence. 
%             Each image is stored in ImData(:,:,i).
%   opt -- options. Usually, default setting is good. No need to specify.
%   opt.K: desired rank of the estimated low-rank component. 
%          Default: \sqrt(min(size(D))) is good generally.
%   opt.lambda: a constant controls the strength of smoothness regularize
%               lambda ~ [1 5] is recommended. Default: 5
%   opt.sigma: STD of noise in the image. If not specified, computed online
%   opt.flagAlign: whether alighment is needed or not.
%   opt.tol: convergence precision. Default: 1e-4
% Output:
%   LowRank -- Low-rank background component
%   Mask -- Segmented object mask
%   tau - transformation parameters to compensate for camera motion
%   info -- other information

disp('^_^^_^^_^^_^^_^^_^ DECOLOR ^_^^_^^_^^_^^_^');
tic;

%% default parameter setting
if ~exist('opt','var'); opt = []; end
if ~isfield(opt,'tol'); opt.tol = 1e-4; end
if ~isfield(opt,'K'); opt.K = floor(sqrt(size(ImData,3))); end
if ~isfield(opt,'lambda'); opt.lambda = 5; end % gamma = opt.lambda * beta;
if ~isfield(opt,'sigma'); opt.sigma = []; end % sigma can be estimated online
if ~isfield(opt,'flagAlign'); opt.flagAlign = false; end % alignment or not

%% variable initialize
ImData = mat2gray(ImData); % 0~1
ImMean = mean(ImData(:));
ImData = ImData - ImMean; % subtract mean is recommended
numImg = size(ImData,3);
sizeImg = [size(ImData,1),size(ImData,2)];
if opt.flagAlign == true && sizeImg(2) > 1
    disp('----------- Pre-alignment ----------');
    [ImTrans,tau] = preAlign(ImData);
    Dtau = reshape(ImTrans,prod(sizeImg),numImg);
else
    tau = [];
    Dtau = reshape(ImData,prod(sizeImg),numImg);
end
maxOuterIts = 20;
alpha = []; % Default setting by soft-impute
beta = 0.5*(std(Dtau(:,1)))^2; % Start from a big value
minbeta = 0.5*(3*std(Dtau(:,1))/20)^2; % lower bound: suppose SNR <= 20
sigma = opt.sigma; % if empty, will be estimated online
B = Dtau; % the low-rank matrix
Omega = true(size(Dtau)); % background support
OmegaOut = false(size(Dtau)); % OmegaOut is to record the extrapolated regions 
ObjArea = sum(~Omega(:));
minObjArea = numel(Dtau(:,1))/1e4; % minimum number of outliers

% graph cuts initialization
% GCO toolbox is called
if opt.lambda > 0
    hMRF = GCO_Create(prod(sizeImg),2);
    GCO_SetSmoothCost( hMRF, [0 1;1 0] );
    AdjMatrix = getAdj(sizeImg);
    amplify = 10 * opt.lambda;
    GCO_SetNeighbors( hMRF, amplify * AdjMatrix );
end

%% outer loop
energy_old = inf; % total energy
for outerIts = 1:maxOuterIts
    disp(['---------------- Outer Loop:  ' num2str(outerIts) ' ----------------']);
    
    %% update tau
    if opt.flagAlign == true && sizeImg(2) > 1
        disp('*** Estimate Transformation ***');
        for i = 1:numImg
            % update once
            [Iwarp,tau(:,i),dummy,Lout] = regImg(reshape(B(:,i),sizeImg),ImData(:,:,i),tau(:,i),double(reshape(Omega(:,i),sizeImg)),1);
            Dtau(:,i) = reshape(Iwarp,prod(sizeImg),1);
            OmegaOut(:,i) = reshape(Lout,prod(sizeImg),1); % extrapolated regions
        end
    end
    
    %% update B
    disp('*** Estimate Low-rank Matrix *** ');
    [B,Bnorm,alpha] = softImpute(Dtau,B,~OmegaOut&Omega,alpha,opt.K);
    E = Dtau - B;
    
    %% estimate sigma 
    if isempty(opt.sigma)
        sigma_old = sigma;
        residue = sort(E(~OmegaOut(:)&Omega(:))); 
        truncate = 0.005; 
        idx1 = round(truncate*length(residue))+1; 
        idx2 = round((1-truncate)*length(residue));
        sigma = std(residue(idx1:idx2));
        if abs(sigma_old-sigma)/abs(sigma_old) < 0.01
            sigma = sigma_old;
        end
    end
    % update beta
    if ObjArea < minObjArea
        beta = beta/2;
    else
        beta = min(max([beta/2,0.5*(3*sigma)^2 minbeta]),beta);
    end
    gamma = opt.lambda * beta;
    
    %% estimate S = ~Omega;
    disp('*** Estimate Outlier Support *** ');
    disp(['$$$ beta = ' num2str(beta) '; gamma = ' num2str(gamma) '; sigma = ' num2str(sigma)]);
    if opt.lambda > 0
        % call GCO to run graph cuts
        energy_cut = 0;
        for i = 1:size(Dtau,2)
            GCO_SetDataCost( hMRF, (amplify/gamma)*[ 0.5*(E(:,i)).^2, ~OmegaOut(:,i)*beta + OmegaOut(:,i)*0.5*max(E(:)).^2]' );
            GCO_Expansion(hMRF);
            Omega(:,i) = ( GCO_GetLabeling(hMRF) == 1 )';
            energy_cut = energy_cut + double( GCO_ComputeEnergy(hMRF) );
        end
        ObjArea = sum(Omega(:)==0);
        energy_cut = (gamma/amplify) * energy_cut;
    else
        % direct hard thresholding if no smoothness
        Omega = 0.5*E.^2 < beta;
        ObjArea = sum(Omega(:)==0);
        energy_cut = 0.5*norm(Dtau-B-E,'fro')^2 + beta*ObjArea;
    end
    
    %% display energy
    energy = energy_cut + alpha * Bnorm;
    disp(['>>> the object area is ' num2str(ObjArea)]);
    disp(['>>> the objectvive energy is ' num2str(energy)]);
    
    %% check termination condition
    if ObjArea > minObjArea && abs(energy_old-energy)/energy < opt.tol; break; end
    energy_old = energy;
    
end

LowRank = uint8(mat2gray(reshape(B,size(ImData))+ImMean)*256);
Mask = reshape(~Omega,size(ImData));

info.opt = opt;
info.time = toc;
info.outerIts = outerIts;
info.energy = energy;
info.rank = rank(B);
info.alpha = alpha;
info.beta = beta;
info.sigma = sigma;

if opt.lambda > 0
    GCO_Delete(hMRF);
end

end



%% function to get the adjcent matirx of the graph
function W = getAdj(sizeData)
numSites = prod(sizeData);
id1 = [1:numSites, 1:numSites, 1:numSites];
id2 = [ 1+1:numSites+1,...
        1+sizeData(1):numSites+sizeData(1),...
        1+sizeData(1)*sizeData(2):numSites+sizeData(1)*sizeData(2)];
value = ones(1,3*numSites);
W = sparse(id1,id2,value);
W = W(1:numSites,1:numSites);
end


%% function for soft-impute
function [Z,Znorm,alpha] = softImpute(X,Z,Omega,alpha0,maxRank)
%
% This program implements the soft-impute algorithm followed by
% postprocessing in the Matrix completion paper Mazumder'10 IJML
% min || Z - X ||_Omega + \alpha || Z ||_Nulear
% \alpha is decrease from alpha0 to the minima value that makes rank(Z) <= maxRank

% X is the incomplete matrix
% maxRank is the desired rank in the constraint
% Omega is the mask with value 1 for data and 0 for missing part
if isempty(Z)
    Z = X;
end
if isempty(Omega)
    Omega = true(size(X));
end
if isempty(alpha0)
    [U,D] = svd(X,'econ'); 
    alpha0 = D(2,2);
end
if isempty(maxRank)
    maxRank = -1;
end
% parameters
eta = 0.707;
epsilon = 1e-4;
maxInnerIts = 20;
%% trivial
% no rank constraint
if maxRank >= min(size(X))
    Z = X;
    [U,D] = svd(Z,'econ');
    Znorm = sum(diag(D));
    alpha = 0;
    return;
end
% no observation
if sum(Omega(:)) == 0
    % no data
    Z = zeros(size(X));
    Znorm = 0;
    alpha = alpha0;
    return;
end
%% soft-impute
% 1. initialize
outIts = 0;
alpha = alpha0;
% 2. Do for alpha = alpha0 > alpha_1 > alpha_2 > ... > alpha_maxRank
disp('begin soft-impute iterations');
while 1
    outIts = outIts + 1;
    energy = inf;
    for innerIts = 1:maxInnerIts
        % (a)i
        C = X.*Omega + Z.*(1-Omega);
        [U,D,V] = svd(C,'econ');
        VT = V';
        % soft impute
        d = diag(D);
        idx = find(d > alpha);
        Z = U(:,idx) * diag( d(idx) - alpha ) * VT(idx,:);
        % (a)ii
        Znorm = sum(d(idx)-alpha);
        energy_old = energy;
        energy = alpha*Znorm + norm(Z(Omega(:))-X(Omega(:)),'fro')/2;
        if abs(energy - energy_old) / energy_old < epsilon
            break
        end
    end
    % check termination condition of alpha
    k = length(idx); % rank of Z
    disp(['alpha = ' num2str(alpha) ';    rank = ' num2str(k) ';  number of iteration: ' num2str(innerIts)]);
    if k <= maxRank && alpha > 1e-3
        alpha = alpha*eta;
    else
        break;      
    end    
end
end