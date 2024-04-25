import matplotlib.pyplot as plt
import pandas as pd


def plot_property_info(df):

    # Convert df columns to numeric
    df['Price'] = pd.to_numeric(df['Price'].str.replace(',', ''),
                                errors='coerce')
    df['Living Space'] = pd.to_numeric(
        df['Living Space'].str.extract(r'(\d+)', expand=False),
        errors='coerce'
    )
    df['Year Built'] = pd.to_numeric(df['Year Built'], errors='coerce')
    df['Rooms'] = pd.to_numeric(df['Rooms'], errors='coerce')

    # Plot Distributions
    plt.figure(figsize=(14, 10))
    plt.suptitle('Distributions')

    ## Price Distributions
    plt.subplot(2, 2, 1)
    df['Price'].plot(kind='hist', bins=20, title='Price',
                     color='seagreen')
    plt.gca().spines[['top', 'right',]].set_visible(False)

    ## Area Distributions
    plt.subplot(2, 2, 2)
    df['Living Space'].plot(kind='hist', bins=20,
                            title='Living Space', color='orange')
    plt.gca().spines[['top', 'right',]].set_visible(False)

    ## No. Rooms Distributions
    plt.subplot(2, 2, 3)
    df['Rooms'].plot(kind='hist', bins=20, title='Rooms',
                     color='lightseagreen')
    plt.gca().spines[['top', 'right',]].set_visible(False)

    ## Year Built Distributions
    plt.subplot(2, 2, 4)
    df['Year Built'].plot(kind='hist', bins=20,
                          title='Year Built', color='salmon')
    plt.gca().spines[['top', 'right',]].set_visible(False)

    # Scatter Plots > relationships between numeric columns
    plt.figure(figsize=(20, 5))
    plt.suptitle('Scatter Plots')

    plt.subplot(1, 3, 1)
    plt.scatter(x=df['Rooms'].astype(float), y=df['Price'].astype(float))
    plt.xlabel('Rooms')
    plt.ylabel('Price')
    plt.title('Rooms vs. Price')

    plt.subplot(1, 3, 2)
    plt.scatter(x=df['Living Space'].astype(float),
                y=df['Price'].astype(float), c='orange')
    plt.xlabel('Living Space')
    plt.ylabel('Price')
    plt.title('Living Space vs. Price')

    plt.subplot(1, 3, 3)
    plt.scatter(x=df['Year Built'].astype(float),
                y=df['Price'].astype(float), c='green')
    plt.xlabel('Year Built')
    plt.ylabel('Price')
    plt.title('Year Built vs. Price')
    plt.show()
