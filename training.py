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
             optimizer: torch.optim.Optimizer, epoch_print: int, writer: torch.utils.tensorboard.writer.SummaryWriter,
             device: torch.device = "cpu"):
    """

    This function trains the model and prints the training and validation loss per epoch.

    :param EPOCHS: int: Number of epochs to train the model.
    :param model: object: Model to train.
    :param train_dataloader: object: Dataloader for the training data.
    :param val_dataloader: object: Dataloader for the validation data.
    :param loss_function: object: Loss function to use.
    :param optimizer: object: Optimizer to use.
    :param epoch_print: int: print each epoch_print epochs.
    :param writer: torch.utils.tensorboard.writer.SummaryWriter: Tensorboard writer.
    :param device: string: Device to use. Defaults to "cpu".
    :return: df_scores: pandas.DataFrame: Dataframe with the training and validation loss per epoch and predictions of the last epoch.
    """

    # print
    print(f"Starting training.")

    # dict with empty lists to store the loss values
    results = {"Epoch": [],
               "Train Loss": [],
               "Validation Loss": [],
               "Train Accuracy": [],
               "Validation Accuracy": []
               }

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

            # divide total validation loss by length of val dataloader: Average validation loss per batch
            batch_val_loss /= len(val_dataloader)
            batch_val_acc /= len(val_dataloader)

        # append the loss values to the lists
        results["Epoch"].append(epoch)
        results["Train Loss"].append(batch_train_loss.detach().cpu().numpy())
        results["Validation Loss"].append(batch_val_loss.detach().cpu().numpy())
        results["Train Accuracy"].append(batch_train_acc.detach().cpu().numpy())
        results["Validation Accuracy"].append(batch_val_acc.detach().cpu().numpy())

        # Add loss results to SummaryWriter
        writer.add_scalars(main_tag="Loss",
                           tag_scalar_dict={"Train Loss": batch_train_loss,
                                            "Validation Loss": batch_val_loss},
                           global_step=epoch)

        # Add accuracy results to SummaryWriter
        writer.add_scalars(main_tag="Accuracy",
                           tag_scalar_dict={"Train Accuracy": batch_train_acc,
                                            "Validation Accuracy": batch_val_acc},
                           global_step=epoch)

        # Track the PyTorch model architecture, and pass in an example input
        writer.add_graph(model=model,input_to_model=torch.randn(32, 3, 224, 224).to(device))

        # print every epochs
        if epoch % epoch_print == 0:
            # print
            print(f"Epoch: {epoch}\n-------")
            print(
                f"Train Loss: {batch_train_loss:.5f} & Accuracy: {batch_train_acc:.5f} | Validation Loss:{batch_val_loss:.5f} & Accuracy: {batch_val_acc:.5f} \n")

    # Close the writer
    writer.close()

    # convert the lists to pandas dataframe for plotting
    df_scores = pd.DataFrame(results)

    # print
    print(f"Finished training.")

    return df_scores

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
