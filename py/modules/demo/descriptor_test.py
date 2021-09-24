from modules.ml import geo_rel_descriptor;
import matplotlib.pyplot as plt;

def main():
    # > Input Generation
    x = [1,2,3,4,5];
    y = [1,2,1,1.5,0.5];
    points_list = [];
    for i in range(len(x)):
        points_list.append([x[i], y[i]]);
    neigh = 2;
    desc = geo_rel_descriptor.compute(points_list,neigh);
    dists = desc[0::2];
    angles = desc[1::2];
    for i in range(len(dists)):
        for j in range(i+1, i+1+neigh ):
            if(j < len(dists)):
                print("> Dist[", i, "->", j , "]:", dists[i]);
                print("> Angle[", i, "->", j, "]:", angles[i]);
    plt.scatter(x,y);
    plt.show();
    return ;
