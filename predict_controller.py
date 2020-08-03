import numpy as np 
import pandas as pd

import matplotlib.pyplot as plt     
import seaborn as sns

from sklearn.linear_model import LinearRegression

dff = pd.DataFrame()

dataset = dff['close'].pct_change()[2:]

#splitting to independent(x) and dependent(y) variables
x=dataset.iloc[:,2].values
y=dataset.iloc[:,3].values


#train and test data split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 1/3, random_state = 0)

#reshaping array to convert from 1D to 2D array
x_test=x_test.reshape(-1,1)
x_train=x_train.reshape(-1,1)

#"lin_reg" is our model calling model "LinearRegression()"
lin_reg=linear_model.LinearRegression()

#fitting our data in linear regression model
lin_reg.fit(x_train,y_train)

#making predictions
lin_reg_pred=lin_reg.predict(x_test)

#coef_ and intercept_ are coefficients and intercepts resp. for our model
print("Coefficients:\n",lin_reg.coef_)
print("Intercept:\n",lin_reg.intercept_)

# The mean squared error
print("Mean squared error: %.2f"
      % mean_squared_error(y_test, lin_reg_pred))

# Explained variance score: 1 is perfect prediction
print('Variance score: %.2f' % r2_score(y_test, lin_reg_pred))

#Plotting the graph for test dataset
plt.scatter(x_test, y_test, color = 'red')
plt.plot(x_test, lin_reg_pred, color = 'blue')
plt.title('Temperature vs Humidity(Test set)')
plt.xlabel('Temperature')
plt.ylabel('Relative Humidity')
plt.show()


# lm=LinearRegression()

# #Loading iris dataset from seaborn library
# iris_data= sns.load_dataset("iris")

# X = iris_data.petal_width.as_matrix(columns=None)
# X=X.reshape(-1, 1)

# #Fitting linear model to predict petal length if petal width is given
# lm=LinearRegression()

# model=lm.fit(X,iris_data.petal_length)


# #User defined function
# def function_predict(petal_width):
#            # convert the input to a number
#            petal_width= int(petal_width)
      
#            #create the prediction data frame
#            prediction_data=pd.DataFrame({'petal_width':[petal_width]})
      
#            # create the prediction
#            return(lm.predict(prediction_data))