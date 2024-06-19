
#plot_data = pd.read_csv('Result/OutputFile.csv', index_col=0)
plot_data=OneDayDF
#plot_data.index = pd.to_datetime(plot_data.index)
plot_data.head()           
if u'Arial' in mpl.rcParams['font.sans-serif']:
    mpl.rcParams['font.sans-serif'].remove(u'Arial')
    mpl.rcParams['font.sans-serif'].insert(0, u'Arial')
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

fig = plt.figure(figsize=(7.16*1.6, 4*1.6)) # make figure 20% too large, to get down to right font size
left, width = 0.06, 0.78
  
     
if methods == ["Negotiator"] or methods == ["Solar"]:
     pass
else:
     temp_ax = fig.add_axes([left, 0.75, width, 0.24]) # left, bottom, width, height
     temp_ax.set_ylabel('$^{\circ}C$')
     temp_ax.yaxis.set_label_coords(-0.053, 0.5)     
     temp_ax.yaxis.set_ticks_position('left')
     
     
actual_temp_ax = fig.add_axes([left, 0.49, width, 0.24])
kwh_ax = fig.add_axes([left, 0.28, width, 0.19])
price_ax = fig.add_axes([left, 0.07, width, 0.19])
# turn off unwanted tick marks and borders
for ax in [actual_temp_ax, kwh_ax, price_ax]:
    ax.yaxis.set_ticks_position('left')
    if ax is not price_ax:
        ax.xaxis.set_visible(False)
boldness= 0.7
try:
   add_plot(actual_temp_ax, 'Act_temp_MILP',label='$T^{tank}, WH-MILP$', color='red', alpha=boldness)
   add_plot(kwh_ax, 'NRG_in_MILP',label='$E^{in},WH-MILP$', color='red', alpha=boldness, linestyle='-.')
   add_plot(temp_ax, 'set_temp_MILP', label='$T^{set}, WH-MILP$', color='red', linestyle='--')
except: pass
try:
   add_plot(actual_temp_ax, 'Act_temp_Negotiator',label='$T^{tank},Negotiator$', color='purple', alpha=boldness)
   add_plot(kwh_ax, 'NRG_in_Negotiator',label='$E^{in},Negotiator$', color='purple', alpha=boldness, linestyle='-.')
   #add_plot(temp_ax, 'set_temp_Negotiator', label='$T^{set}, Negotiator$', color='purple', linestyle='--')   
except: pass
try:
   add_plot(actual_temp_ax, 'Act_temp_Solar',label='$T^{tank}, Solar-MILP$', color='orange', alpha=boldness)
   add_plot(kwh_ax, 'NRG_in_Elec',label='$E^{Elec},Solar-MILP$', color='brown', alpha=boldness, linestyle='-.')
   add_plot(kwh_ax, 'NRG_in_Solar',label='$E^{Solar},Solar-MILP$', color='orange', alpha=boldness, linestyle='-.')
   add_plot(temp_ax, 'set_temp_Solar', label='$T^{set}, Solar-MILP$', color='orange', linestyle='--')
except: pass
try:
   add_plot(actual_temp_ax, 'Act_temp_Apt',label='$T^{tank}, Apt&Goh$', color='green', alpha=boldness)
   add_plot(kwh_ax, 'NRG_in_Apt',label='$E^{in},Apt&Goh$', color='green', alpha=boldness, linestyle='-.')
   add_plot(temp_ax, 'set_temp_Apt', label='$T^{set}, Apt&Goh$', color='green', linestyle='--')
except: pass
try:     
   add_plot(kwh_ax, 'NRG_in_Du',label='$E^{in},Du&Lu$', color='blue', alpha=boldness, linestyle='-.')
   add_plot(actual_temp_ax, 'Act_temp_Du',label='$T^{tank}, Du&Lu$', color='blue', alpha=boldness)
except: pass
try:   
   add_plot(kwh_ax, 'NRG_in_Fixed',label='$E^{in},Fixed \enspace Setpoint$', color='gray', alpha=boldness, linestyle='-.')     
   add_plot(actual_temp_ax, 'Act_temp_Fixed',label='$T^{tank}, Fixed \enspace Setpoint$', color='gray', alpha=boldness)
except: pass
try:
   add_plot(actual_temp_ax, 'Act_temp_EA_GA',label='$T^{tank}, EA_GA$', color='cyan', alpha=boldness)
   add_plot(kwh_ax, 'NRG_in_EA_GA',label='$E^{in},EA_GA$', color='cyan', alpha=boldness, linestyle='-.')
   add_plot(temp_ax, 'set_temp_EA_GA', label='$T^{set}, EA_GA$', color='cyan', linestyle='--')
except: pass


add_plot(price_ax, "Price" ,label='$P^{p}$', color='black', linewidth=4)
add_plot(kwh_ax, 'NRG_Req',label='$e^{des}$',color='black', alpha=1, linestyle=':', linewidth=1.5)
if 'Solar' in methods:
    add_plot(kwh_ax, 'Solar',label='$e^{Solar}$',color='yellow', alpha=0.9, linewidth=2.5)


    
     
kwh_ax.set_ylabel('kWh')
price_ax.set_ylabel('$/MWh')             
actual_temp_ax.set_ylabel('$^{\circ}C$')


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

if os.name == 'nt':  # Windows
    output_dir = 'Graphs\\OneDay'
else:  # macOS/Linux
    output_dir = 'Graphs/OneDay'

# Ensure the directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Debugging: print the absolute path to ensure correctness
absolute_output_dir = os.path.abspath(output_dir)

if len(sys.argv) == 1:
    save_path = os.path.join(absolute_output_dir, '({}, {})Daily.svg'.format(current_day, penalty_vector[j]))
    print(f"Saving to file: {save_path}")  # Debugging: print the save path
    fig.savefig(save_path)
    
fig.show()
#fig.close()            
print("--- %s seconds for total Run" % (time.time() - start_time))            