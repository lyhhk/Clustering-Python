import numpy as np
import collections


def alias_setup(probs):
    """
    probs： 某个概率分布
    返回: Alias数组与Prob数组
    """
    K = len(probs)
    q = np.zeros(K)
    J = np.zeros(K, dtype=np.int)
    # Sort the data into the outcomes with probabilities
    # that are larger and smaller than 1/K.
    smaller = []
    larger = []
    for i, prob in enumerate(probs):
        q[i] = K * prob  # 概率
        if q[i] < 1.0:
            smaller.append(i)
        else:
            larger.append(i)

    # Loop though and create little binary mixtures that
    # appropriately allocate the larger outcomes over the
    # overall uniform mixture.
    while len(smaller) > 0 and len(larger) > 0:
        small = smaller.pop()
        large = larger.pop()

        J[small] = large
        q[large] = q[large] - (1.0 - q[small])

        if q[large] < 1.0:
            smaller.append(large)
        else:
            larger.append(large)

    return J, q


def alias_draw(J, q):
    '''
    输入: Prob数组和Alias数组
    输出: 一次采样结果
    '''
    K = len(J)
    # Draw from the overall uniform mixture.
    k = int(np.floor(np.random.rand() * K))  # 随机取一列

    # Draw from the binary mixture, either keeping the
    # small one, or choosing the associated larger one.
    if np.random.rand() < q[k]:
        return k
    else:
        return J[k]


def alias_sample(probs, samples):
    assert isinstance(samples, int), 'Samples must be a integer.'
    sample_result = []
    J, p = alias_setup(probs)
    for i in range(samples):
        sample_result.append(alias_draw(J, p))
    return sample_result


def choose_centers(dataset, k):
    center_ids = [np.random.choice(len(dataset), size=1)]
    dist_mat = np.empty(shape=[len(dataset), len(dataset)])
    for i in range(len(dataset)):
        for j in range(len(dataset)):
            if i == j:
                dist_mat[i, j] = 0.
            elif i < j:
                dist_mat[i, j] = np.mean(np.square(dataset[i] - dataset[j]))
            else:
                dist_mat[i, j] = dist_mat[j, i]
    while len(center_ids) < k:
        nodes_min_dist = np.min(dist_mat[:, center_ids], axis=1)
        probs = nodes_min_dist / np.sum(nodes_min_dist)
        center_ids.append(alias_sample(probs.reshape(-1), 1))
    center_ids = np.array(center_ids).reshape(-1)
    return center_ids


def do_cluster(dataset, centers):
    dist = []
    for center in centers:
        dist.append(np.mean(np.square(dataset - center), axis=1))
    dist = np.vstack(dist)
    classes = np.argmin(dist, axis=0)
    return classes


def show_result(class_list, raw_data, center_coordinate):
    colors = [
              '#FF0000', '#FFA500', '#FFFF00', '#00FF00', '#228B22',
              '#0000FF', '#FF1493', '#EE82EE', '#000000', '#FFA500',
              '#00FF00', '#006400', '#00FFFF', '#0000FF', '#FFFACD',
              ]

    # 画最终聚类效果图
    use_color = {}
    total_color = list(dict(collections.Counter(class_list)).keys())
    for index, i in enumerate(total_color):
        use_color[i] = index
    plt.figure(num=1, figsize=(16, 9))
    for index, point in enumerate(class_list):
        plt.scatter(x=raw_data[index, 0], y=raw_data[index, 1], c=colors[use_color[point]], s=50, marker='o', alpha=0.9)
    plt.scatter(x=center_coordinate[:, 0], y=center_coordinate[:, 1], c='b', s=200, marker='+', alpha=0.8)
    plt.title('The Result Of Cluster')
    plt.savefig('./kmeans++_result.jpg')
    plt.show()
    
    
 def kmeans_plus_plus(dataset, k):
    if not isinstance(dataset, np.ndarray):
        dataset = np.array(dataset)
    center_ids = choose_centers(dataset, k)
    centers = dataset[center_ids]
    classes_before = np.arange(len(dataset))
    while True:
        classes_after = do_cluster(dataset, centers)
        if (classes_before == classes_after).all():
            break

        classes_before = classes_after
        for c in range(k):
            data_c = dataset[np.argwhere(classes_after == c)]
            center_c = np.mean(data_c, axis=0)
            centers[c] = center_c

    return centers, classes_after


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    data_path = 'xxx/Aggregation.txt'
    data = np.loadtxt(data_path, delimiter='	', usecols=[0, 1], dtype=np.float32)
    centers, classes = kmeans_plus_plus(data, 7)
    show_result(classes, data, centers)
