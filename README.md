First I created a model with 2D convolutional layer with 5 filters. I kept a max-pooling
layer with pool-size (2, 2) and and flattened it. Output layer used "softmax" activation
to achieve a probability distribution. I did not initially add any hidden layers and that
way model seemed to get around 97-99 % accuracy for the smaller dataset. I tried to add a
hidden layer with double the number of units compared to the size of output vector. Then,
model turned out lose its accuracy even during training to around 65 % even after adding a
dropout to the model. I tried changing the activation function and add some regularization
but it did not have much effect. Seeing that my dataset is size of 3 causing the hidden
layer to have input size less than 10, only once I increased its size to anything around
20 and above, I seemed to get the model to ever have accuracy above 90 %. This was though
unreliable and I just increased it to 100 and thus far it seems to do good enough job. In
the real world, I should probably add even more units. Running this model with bigger data
set does not achieves great accuracy at all. I had to add another convolution layer (without
pooling) to achieve any consistently good results with the bigger dataset.
I also increased the filter count for both convolution layers (first 16 -> second 32).

What I noticed

- Hidden layers need enough units to be able to differentiate the input data.
- Only quite small amount of convolution filters was enough to differentiate small datasets.
- For bigger datasets, using more convolution layers tended to achieve better differentiation.
- There is some randomness each time a model is created. This is due to local minimums?
