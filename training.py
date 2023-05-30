"""
Name: training.py in Project: PytorchIntroduction
Author: Simon Leiner
Date: 28.05.23
Description: This file contains the batch training script
"""

import pandas as pd
import torch
from tqdm.auto import tqdm
import torchmetrics


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Checked: Function works

def training(EPOCHS: int, model: torch.nn.Module, train_dataloader: torch.utils.data.DataLoader,
             val_dataloader: torch.utils.data.DataLoader, loss_function: torch.nn.Module,
             optimizer: torch.optim.Optimizer, epoch_print: int, device: torch.device = "cpu"):
    """

    This function trains the model and prints the training and validation loss per epoch.

    :param EPOCHS: int: Number of epochs to train the model.
    :param model: object: Model to train.
    :param train_dataloader: object: Dataloader for the training data.
    :param val_dataloader: object: Dataloader for the validation data.
    :param loss_function: object: Loss function to use.
    :param optimizer: object: Optimizer to use.
    :param epoch_print: int: print each epoch_print epochs.
    :param device: string: Device to use. Defaults to "cpu".
    :return: df_scores, df_predictions : pandas.DataFrame: Dataframe with the training and validation loss per epoch and predictions of the last epoch.
    """

    # print
    print(f"Starting training.")

    # empty lists to store the loss values
    train_loss_values = []
    val_loss_values = []
    train_acc_values = []
    val_acc_values = []
    epoch_count = []
    train_pred = []
    train_true = []
    val_pred = []
    val_true = []

    # create a training and test loop
    for epoch in tqdm(range(EPOCHS)):

        # train loss counter
        batch_train_loss, batch_train_acc = 0, 0

        # model to train mode
        model.train()

        # training: loop thorugh the training batches
        for batch, (X_train, y_train) in enumerate(train_dataloader):

            # put data on device
            X_train, y_train = X_train.to(device), y_train.to(device)

            # calculate the forward pass
            y_pred_train = model(X_train)

            # calculate the training loss and add (accumulate) the loss to the counter
            training_loss = loss_function(y_pred_train, y_train)
            batch_train_loss += training_loss
            batch_train_acc += torchmetrics.functional.accuracy(preds=y_pred_train.argmax(dim=1), target=y_train,
                                                                task="multiclass", num_classes=y_pred_train.shape[1])

            # append predictions and true values in the last epoch
            if epoch == EPOCHS - 1:
                train_pred.append(y_pred_train.detach().cpu().numpy())
                train_true.append(y_train.detach().cpu().numpy())

            # optimizer zero grad
            optimizer.zero_grad()

            # calcuate the loss backwards (backpropagation)
            training_loss.backward()

            # optimizer step
            optimizer.step()

        # divide total train loss by length of train dataloader: Average training loss per batch
        batch_train_loss /= len(train_dataloader)
        batch_train_acc /= len(train_dataloader)

        # validation loss counter
        batch_val_loss, batch_val_acc = 0, 0

        # model to validation mode
        model.eval()

        # inference mode diasables gradient tracking
        with torch.inference_mode():

            # validation: loop thorugh the validation batches
            for batch, (X_val, y_val) in enumerate(val_dataloader):

                # put data on device
                X_val, y_val = X_val.to(device), y_val.to(device)

                # calculate the forward pass
                y_pred_val = model(X_val)

                # calculate the validation loss and add (accumulate) the loss to the counter
                val_loss = loss_function(y_pred_val, y_val)
                batch_val_loss += val_loss
                batch_val_acc += torchmetrics.functional.accuracy(preds=y_pred_val.argmax(dim=1), target=y_val,
                                                                  task="multiclass", num_classes=y_pred_val.shape[1])

                # append predictions and true values in the last epoch
                if epoch == EPOCHS - 1:
                    val_pred.append(y_pred_val.detach().cpu().numpy())
                    val_true.append(y_val.detach().cpu().numpy())

            # divide total validation loss by length of val dataloader: Average validation loss per batch
            batch_val_loss /= len(val_dataloader)
            batch_val_acc /= len(val_dataloader)

        # append the loss values to the lists
        epoch_count.append(epoch)
        train_loss_values.append(batch_train_loss.detach().cpu().numpy())
        val_loss_values.append(batch_val_loss.detach().cpu().numpy())
        train_acc_values.append(batch_train_acc.detach().cpu().numpy())
        val_acc_values.append(batch_val_acc.detach().cpu().numpy())

        # print every epochs
        if epoch % epoch_print == 0:
            # print
            print(f"Epoch: {epoch}\n-------")
            print(
                f"Train Loss: {batch_train_loss:.5f} & Accuracy: {batch_train_acc:.5f} | Validation Loss:{batch_val_loss:.5f} & Accuracy: {batch_val_acc:.5f} \n")

    # convert the lists to pandas dataframe for plotting
    df_scores = pd.DataFrame({"Epoch": epoch_count, "Train Loss": train_loss_values, "Validation Loss": val_loss_values,
                              "Train Accuracy": train_acc_values, "Validation Accuracy": val_acc_values})

    # convert the predictions to pandas dataframe
    df_train_predictions = pd.DataFrame({"Train Predictions": train_pred, "Train True Values": train_true})

    # convert the predictions to pandas dataframe
    df_val_predictions = pd.DataFrame({"Val Predictions": val_pred, "Val True Values": val_true})

    # print
    print(f"Finished training.")

    return df_scores, df_train_predictions, df_val_predictions

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
