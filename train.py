from funcs_train import *

path_data = "/data2/noses_data/cnn_data/"

<<<<<<< HEAD
""" Load in images and bounding box meta data """

imgs = np.load(path_data + "images_medium.npy", allow_pickle=True)
bb_data = np.load(path_data + "bb_data_medium.npy", allow_pickle=True)
print("images shape:", imgs.shape)
print("bb_data shape:", bb_data.shape)
=======
"""## Functions"""

def preprocessing(X_init, y_init):
  X_init = X_init[:] / 255.
  y_init = y_init[:] / 1.

  X = []
  y = []
  for Xi, yi in zip(X_init, y_init):
    im = tf.image.resize(Xi, (96, 96))
    X.append(im)
    y.append(yi)

  X = tf.stack(X)
  y = tf.stack(y)
  return X, y

# given X and y data, returns newly shuffled X and y data
# def shuffle_xy(X, y):
#   indices = tf.range(start=0, limit=tf.shape(Xtrain)[0], dtype=tf.int32)
#   shuffled_indices = tf.random.shuffle(indices)
#   X_shuffled = tf.gather(X, shuffled_indices)
#   y_shuffled = tf.gather(y, shuffled_indices)
#   return X_shuffled, y_shuffled

"""## Load in images and bounding box meta data"""

imgs = np.load(path_data + "images.npy", allow_pickle=True)
bb_data = np.load(path_data + "bb_data.npy", allow_pickle=True)

imgs.shape, bb_data.shape

"""### Extract tertiary labels
- 0 for "no seal"
- 1 for "partial seal"
- 2 for "full seal"
"""

def get_seal_percent(df_subimg):
  seal_percent = 0
  for i in df_subimg.itertuples():
    #print(i)
    seal_percent += i[3] # have to add for cases where multiple seals are present
  return seal_percent

def get_labels(bb_data, threshold = 1):
  labels = []
  for df_subimg in bb_data:
    if not isinstance(df_subimg, type(None)):
      seal_percent = get_seal_percent(df_subimg)
      if seal_percent > threshold:
        val = 2
      else:
        val = 1
    else:
      val = 0
    labels.append(val)
  labels = np.array(labels)
  return labels

>>>>>>> 9dde381afeb2d96e4c77a82bb524599f1c31af37

"""  Extract labels """
labels = get_labels_binary(bb_data)

<<<<<<< HEAD
=======
def get_xy_indices(bb_data, test_frac = .1):
  # get indices for images w seals
  indices_w_seal = []
  for i in range(len(bb_data)):
    if not bb_data[i] is None:
      indices_w_seal.append(i)

  num_w_seal = len(indices_w_seal)
  size_dataset = int(num_w_seal * 10/4) # size for dataset with 40% of images containing seals
  num_wo_seal = size_dataset - num_w_seal

  # get indices for images w/o seals
  all_indices_wo_seal = [x for x in list(range(len(bb_data))) if x not in indices_w_seal]
  indices_wo_seal = random.sample(all_indices_wo_seal, num_wo_seal)

  print("num sub images for dataset with 40% images containing seals", size_dataset)
  print("num sub images with a seal", num_w_seal)
  print("num sub images without a seal", num_wo_seal)
  print()

  num_train_w_seal = round((1 - test_frac) * num_w_seal)
  num_train_wo_seal = round((1 - test_frac) * num_wo_seal)

  # train test split of indices, each with 40% of sub imgs containing seals
  train_indices = np.concatenate((np.array(indices_w_seal[:num_train_w_seal]),
                                  np.array(indices_wo_seal[:num_train_wo_seal])))
  test_indices = np.concatenate((np.array(indices_w_seal[num_train_w_seal:]),
                                  np.array(indices_wo_seal[num_train_wo_seal:])))
  return train_indices, test_indices

def create_model(cnn_blocks=1, dense_layers=1, filter_multiplier = 1,
                 kernel_size=3, strides=(1, 1), dense_output_size =1024):
  model = keras.models.Sequential()
  for i in range(cnn_blocks):
    conv_output_dim = int((conv_dim_init * filter_multiplier) * (i + 1))
    model.add(layers.Conv2D(filters=conv_output_dim, kernel_size=kernel_size,
                            strides=strides, activation='relu',padding='same'))
    model.add(layers.Conv2D(filters=conv_output_dim, kernel_size=kernel_size,
                            strides=strides, activation='relu',padding='same'))
    model.add(layers.MaxPooling2D(2, 2))
  model.add(layers.Flatten())
  for i in range(dense_layers):
    model.add(layers.Dense(units=dense_output_size , activation='relu'))
  model.add(layers.Dense(3, activation='softmax',name='z'))

  opt = tf.keras.optimizers.Adam(lr=lr) #sgd
  model.compile(loss='sparse_categorical_crossentropy',optimizer=opt,metrics='accuracy')
  return model

#@tf.function(input_signature=(tf.TensorSpec(shape=[None], dtype=tf.int32),))
def run_model(cnn_blocks, dense_layers, filter_multiplier,
              kernel_size, strides, dense_output_size):
  model = create_model(cnn_blocks, dense_layers, filter_multiplier, kernel_size, strides, dense_output_size)
  model.fit(Xtrain, ytrain, batch_size=batch_size, epochs=epochs,
            validation_split=.1, verbose=True)
  res = model.evaluate(Xtest, ytest); loss = res[0]; acc = res[1]
  ypred = model.predict(Xtest)
  print("%d CCP Block(s), %d Dense Layer(s), %fx Filter Multiplier, %d Kernel Size, %s Strides, %d Dense Output Size" %
        (cnn_blocks, dense_layers, filter_multiplier, kernel_size, strides, dense_output_size),
        "\nLoss:       %f\nAccuracy:   %f" % (loss, acc))
  return ypred

# convert ypred back to predictions of 0, 1, 2
# convert ytest from tensor to list
def convert_arrs(ypred, ytest):
  ypred_ = []
  for i in range(len(ypred)):
    confidence_arr = list(ypred[i])
    ypred_.append(np.argmax(confidence_arr))
  ytest_ = []
  for i in range(len(ytest)):
    ytest_.append(int(ytest[i]))
  return ypred_, ytest_

def print_metrics(ypred, ytest):
  ypred_, ytest_ = convert_arrs(ypred, ytest)
  f1 = f1_score(np.array(ytest_), ypred_, labels=np.unique(ytest_), average="weighted")
  precision = precision_score(np.array(ytest_), ypred_, labels=np.unique(ypred_), average="weighted")
  recall = recall_score(np.array(ytest_), ypred_, labels=np.unique(ypred_), average="weighted")
  print("F1 Score:  ", f1)
  print("Precision: ", precision)
  print("Recall:    ", recall)
  print("Confusion Matrix:")
  print(pd.crosstab(pd.Series(ytest_), pd.Series(ypred_), rownames=['Actual'], colnames=['Predicted'], margins=True), "\n")
>>>>>>> 9dde381afeb2d96e4c77a82bb524599f1c31af37

"""## Grid Search
Paramterers:
- Number of Conv-Conv-Pool (CCP) blocks
- Number of Dense layers
- Kernel Size: specifies height and width of convolution window
- Strides: specifies the strides of the convolution along the height and width
- Dense Ouput Size: size of output space for the dense layer(s)
"""

<<<<<<< HEAD
# cnn_blocks_grid = [1, 2, 3]
# dense_layers_grid = [1, 2, 3]
# filter_multiplier_grid  = [.5, 1, 2]
# kernel_size_grid = [2, 3, 4]
# strides_grid = [(1, 1), (2, 2), (3, 3)]
# dense_output_size_grid = [1024, 2048, 4096]

cnn_blocks_grid = [3]
dense_layers_grid = [1]
filter_mult_grid  = [.5]
kernel_size_grid = [2]
strides_grid = [(5, 5)]
dense_size_grid = [128]
threshold_min_grid = [.1]

model_params_grid = list(itertools.product(cnn_blocks_grid, dense_layers_grid,
                                        filter_mult_grid, kernel_size_grid,
                                        strides_grid, dense_size_grid,
                                        threshold_min_grid))
for model_params in model_params_grid:
    cnn_blocks = model_params[0]; dense_layers = model_params[1]; filter_mult = model_params[2]
    kernel_size = model_params[3]; strides = model_params[4]; dense_size= model_params[5]
    threshold_min = model_params[6]
    Xtrain, ytrain, Xtest, ytest, seal_percents = train_test_split(imgs, bb_data, labels, threshold_min)
    ypred = run_model(Xtrain, ytrain, Xtest, ytest,
                        cnn_blocks, dense_layers, filter_mult, kernel_size,
                        strides, dense_size, threshold_min)
    ypred_, ytest_ = print_metrics(ypred, ytest)

fname = "acc_buckets_plot.png"
plot_acc_buckets(ytest_, ypred_, seal_percents, fname)
=======
# test different thresholds for the image classification
thresholds = [0.8, 0.9, 1.0]

for thres in thresholds:
  print("Threshold: ", thres)
  labels = get_labels(bb_data, thres)
  # TODO: ask Dr. Dekyhtar how to handle situation where two seals are present in a subimage

  pd.Series(labels).value_counts()

  train_indices, test_indices = get_xy_indices(bb_data)

  Xtrain, ytrain = preprocessing(imgs[train_indices], labels[train_indices])
  Xtest, ytest = preprocessing(imgs[test_indices], labels[test_indices])

  print("train dims:", Xtrain.shape, ytrain.shape)
  print("test dims:", Xtest.shape, ytest.shape)
  print()

  """## Training"""

  lr = 3e-4
  batch_size = 32
  conv_dim_init = 64
  epochs = 1


  cnn_blocks_grid = [1, 2, 3]
  dense_layers_grid = [1]
  filter_multiplier_grid  = [.5, 1]
  kernel_size_grid = [2, 3]
  strides_grid = [(1, 1)]
  dense_output_size_grid = [1024, 2048]

  for cnn_blocks in cnn_blocks_grid:
    for dense_layers in dense_layers_grid:
      for filter_multiplier in filter_multiplier_grid:
        for kernel_size in kernel_size_grid:
          for strides in strides_grid:
            for dense_output_size in dense_output_size_grid:
              ypred = run_model(cnn_blocks, dense_layers, filter_multiplier,
                                kernel_size, strides, dense_output_size)
              print_metrics(ypred, ytest)

#print(len(ypred_))
#print(len(ytest_))

# check accuracy
# count = 0
# length = len(ypred_)
# for i in range(length):
#   if ypred_[i] == ytest_[i]:
#     count += 1
#
# acc = count/length
# print("Model Accuracy: ", acc)

>>>>>>> 9dde381afeb2d96e4c77a82bb524599f1c31af37

"""## Evaluation"""

"""
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.xlabel('iteration')
plt.ylabel('loss')
plt.title('Loss over time')
plt.legend(['train','val'])
plt.show()

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.xlabel('iteration')
plt.ylabel('acc')
plt.title('Accuracy over time')
plt.legend(['train','val'])
plt.show()
"""
