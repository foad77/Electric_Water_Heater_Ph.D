

#plot_data = pd.read_csv('Result/OutputFile.csv', index_col=0)
plot_data=OneDayDF
#plot_data.index = pd.to_datetime(plot_data.index)
plot_data.head()           

plot_data.Price=[24,23,22,21,20,20.5,21,21.5,22,22.5,23,23.5,24,24.5,25,25.5,26,27.5,29,30.5,32,30,27,24.5]
plot_data.Solar=[0,0,0,0,0,0,0.9,2.3,4.3 ,5.7,7,8.3,7.2,5.5,4,2.7,0.9,0,0,0,0,0,0,0]
plot_data.NRG_Req=plot_data.Price-plot_data.Solar
# if u'Arial' in mpl.rcParams['font.sans-serif']:
#     mpl.rcParams['font.sans-serif'].remove(u'Arial')
#     mpl.rcParams['font.sans-serif'].insert(0, u'Arial')


    
tags = ['WH-MILP', 'Du&Lu','Apt&Goh']
tc = zip(tags[:3], ['red', 'blue','green'])  # tag, color pairs to plot
lines = [];labels = []


def add_plot(ax, col, fill=False ,**kwargs):
    settings = dict(label=col, linewidth=1, drawstyle='steps-post')
    settings.update(kwargs)
    if fill:
        area_settings = settings.copy()      
        area_settings['linestyle'] = 'None'
        del area_settings['drawstyle'] # not supported
        ax.fill_between(plot_data.index, 0, plot_data[col], **area_settings)
    else:
        labels.append(settings['label'])
        lines.append(ax.plot(plot_data[col], **settings)[0])



fig = plt.figure(figsize=(7, 2)) # make figure 20% too large, to get down to right font size
left, width = 0.07, 0.75
temp_ax = fig.add_axes([left, 0.1, width, 0.88]) # left, bottom, width, height



# for ax in [temp_ax, actual_temp_ax, kwh_ax, price_ax]:
#     ax.yaxis.set_ticks_position('left')
#     if ax is not price_ax:
#         ax.xaxis.set_visible(False)
boldness= 0.7

ax.xaxis.set_visible(True)

add_plot(temp_ax, "Price" ,label='$overal load$', color='blue', linestyle=':', linewidth=1)
add_plot(temp_ax, 'NRG_Req',label='$net Load$',color='red', alpha=0.9, linewidth=1.5)
if 'Solar' in methods:
    add_plot(temp_ax, 'Solar',label='$Solar$',color='yellow', alpha=0.85, linewidth=2.5)


temp_ax.set_ylabel('$Kwh$')

# kwh_ax.set_ylabel('kWh')
# price_ax.set_ylabel('$/MWh')             
# actual_temp_ax.set_ylabel('$^{\circ}C$')

temp_ax.yaxis.set_label_coords(-0.065, 0.5)
for ax in [kwh_ax, price_ax, actual_temp_ax]:
    ax.yaxis.set_label_coords(-0.06, 0.5)

for ax in fig.axes:
    ax.legend(bbox_to_anchor=(1.0, 0.5), loc="center left",frameon=False)
# temp_ax.legend(bbox_to_anchor=(1.0, 1.0), loc="upper left",frameon=False)

fig.canvas.draw()
# shorten day-of-week names
x_labels = [x.get_text() for x in actual_temp_ax.get_xticklabels()]
x_labels = [t[:2]+t[3:] for t in x_labels] # drop third character
actual_temp_ax.set_xticklabels(x_labels)

if len(sys.argv) == 1:
  fig.savefig('Graphs/OneDay/duckcurve.svg'.format(current_day,penalty_vector[j]))
fig.show()
#fig.close()            
print("--- %s seconds for total Run" % (time.time() - start_time))            