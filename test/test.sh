set -e

# setup search space
clerk clerk-config -w w0 -ss clerk -ws mnli
clerk search-setup train_loss=[] test_acc=[] lr=[1e-4,5e-5,3e-5,2e-5,1e-5] bs=[16,32] wr=[0.1,0.06]
 

python notrain.py

clerk add-log test_acc=0.2 train_lose=0.5
clerk new-run

python notrain.py $(clerk get-args lr bs wr)
clerk new-run
