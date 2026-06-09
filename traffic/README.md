First I created a model with 2D convolutional layer with 5 filters. I kept a max-pooling
layer with pool-size (2, 2) and and flattened it. Output layer used "softmax" activation
to achieve a probability distribution. I did not initially add any hidden layers and that
way model seemed to get around 97-99 % accuracy for the smaller dataset. I tried to add a
hidden layer with double the number of units compared to the size of output vector. Then,
model turned out lose its accuracy even during training to around 65 % even after adding a
dropout to the model. I tried changing the activation function and add some regularization
but it did not have much effect. It seems that model was not able create enough seperation
for the images with such little convolution.

Running this model with bigger data set did not achieve great accuracy at all. I had to
add at least one another convolution layer to achieve any consistently good results with the
bigger dataset. I also increased the amount of filtering done at each convolution layer.

What I noticed

- Hidden layers need enough units to be able to differentiate the input data.
- It seems after each pooling, you should ~2x the number of filtering for next convolution.
- Only quite small amount of convolution filters was enough to differentiate small datasets.
- For bigger datasets, adding more convolutional layers achieves better seperation.
- There is some randomness each time a model is created. This is due to local minimums?
