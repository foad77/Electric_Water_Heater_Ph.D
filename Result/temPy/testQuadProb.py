from gapminder import gapminder
gapminder.head()



fig, ax = plt.subplots(figsize=(10, 5))

years = scatter_data['year'].unique()

colors =[f'C{i}' for i in np.arange(1, 6)]
cmap, norm = matplotlib.colors.from_levels_and_colors(np.arange(1, 5+2), colors)


label = ax.text(0.95, 0.25, years[0],
                horizontalalignment='right',
                verticalalignment='top',
                transform=ax.transAxes,
                fontdict=font)


def update_scatter(i):

    year = years[i]

    data_temp = scatter_data.loc[scatter_data['year'] == year, :]
    ax.clear()
    label = ax.text(0.95, 0.20, years[i],
                horizontalalignment='right',
                verticalalignment='top',
                transform=ax.transAxes,
                fontdict=font)
    ax.scatter(
        data_temp['gdpPercap'],
        data_temp['lifeExp'],
        s=data_temp['pop']/500000, 
        alpha = 0.5, 
        c=data_temp.color, 
        cmap=cmap,
        norm=norm
    )

    label.set_text(year)

anim = animation.FuncAnimation(fig, update_scatter, frames = len(years), interval = 30)
anim.save('scatter.gif') 










##========================================



barchartrace_data  = gapminder.copy()
n_observations = 10

fig, ax = plt.subplots(figsize=(10, 5))

font = {
    'weight': 'normal',
    'size'  :  40,
    'color': 'lightgray'
}

years = barchartrace_data['year'].unique()

label = ax.text(0.95, 0.20, years[0],
                horizontalalignment='right',
                verticalalignment='top',
                transform=ax.transAxes,
                fontdict=font)


def update_barchart_race(i):

    year = years[i]

    data_temp = barchartrace_data.loc[barchartrace_data['year'] == year, :]

    # Create rank and get first 10 countries
    data_temp['prueba'] = data_temp['gdpPercap'].rank(ascending = False)
    data_temp = data_temp.loc[data_temp['prueba'] <= n_observations]

    colors = plt.cm.Dark2(range(6))

    ax.clear()
    ax.barh(y = data_temp['prueba'] ,
            width = data_temp.gdpPercap, 
            tick_label=data_temp['country'],
           color=colors)

    label = ax.text(0.95, 0.20, year,
                horizontalalignment='right',
                verticalalignment='top',
                transform=ax.transAxes,
                fontdict=font)

    ax.set_ylim(ax.get_ylim()[::-1]) # Revert axis


anim = animation.FuncAnimation(fig, update_barchart_race, frames = len(years))
anim.save('barchart_race.gif') 