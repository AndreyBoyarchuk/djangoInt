import datapane as dp

report = dp.Report(
    dp.Text("Hello, Datapane!")
)

report.publish(name='My Report')
