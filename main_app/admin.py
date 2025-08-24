from django.contrib import admin

from main_app.models import InvalidSMSContribution, SMSContribution, Sponsor, Station

# Register your models here.


class SMSContributionAdmin(admin.ModelAdmin):
    search_fields = [
        "id",
        "contributor_id",
        "station__id",
        "water_height",
        "temperature",
        "date_received",
    ]
    list_filter = ["station"]
    list_display = [
        "id",
        "contributor_id",
        "water_height",
        "temperature",
        "station",
        "date_received",
    ]
    ordering = ("-date_received",)


class InvalidSMSContributionAdmin(admin.ModelAdmin):
    search_fields = ["contributor_id", "message_body"]
    list_display = ["contributor_id", "message_body", "date_received"]
    ordering = ("-date_received",)


class StationAdmin(admin.ModelAdmin):
    search_fields = ["id", "name", "state"]
    list_filter = ["status", "water_body_type", "state"]
    list_display = ["id", "name", "state", "water_body_type", "status", "date_added"]
    list_editable = ["status"]

    # def save_model(self, request, obj, form, change):
    #     test_csv_file = Path(
    #         ("/htdocs/www/crowdhydrology_driver/data/" + obj.id.upper() + ".csv")
    #     )
    #     if not test_csv_file.is_file():
    #         csv_file = open(
    #             "/htdocs/www/crowdhydrology_driver/data/" + obj.id.upper() + ".csv", "w"
    #         )
    #         csv_file.write("Date and Time,Gage Height (ft),POSIX Stamp\n")

    #     test_dygraph_file = Path(
    #         (
    #             "/htdocs/www/crowdhydrology_driver/charts/"
    #             + obj.id.upper()
    #             + "_dygraph.html"
    #         )
    #     )
    #     if not test_dygraph_file.is_file():
    #         dygraph_file = open(
    #             "/htdocs/www/crowdhydrology_driver/charts/"
    #             + obj.id.upper()
    #             + "_dygraph.html",
    #             "w",
    #         )
    #         dygraph_file.write(
    #             """<!DOCTYPE html>
    #         <html>
    #           <head>
    #             <meta http-equiv="X-UA-Compatible" content="IE=EmulateIE7; IE=EmulateIE9">
    #             <!--[if IE]><script src="js/graph/excanvas.js"></script><![endif]-->
    #           </head>
    #           <body>
    #             <script src="js/graph/dygraph-combined.js" type="text/javascript"></script>
    #               <div id="graphdiv"></div>
    #         <script>
    #                 g = new Dygraph(
    #                 document.getElementById("graphdiv"),
    #                 "../data/"""
    #             + obj.id.upper()
    #             + """.csv",
    #                 {   title: "Hydrograph at """
    #             + obj.id.upper()
    #             + """",
    #                 labelsDivStyles: { 'textAlign': 'right' },
    #                 showRoller: true,
    #                 xValueFormatter: Dygraph.dateString_,
    #                 xTicker: Dygraph.dateTicker,
    #                 labelsSeparateLines: true,
    #                 labelsKMB: true,
    #                 visibility: [true,false],
    #                 drawXGrid: false,
    #                  width: 640,
    #                 height: 300,
    #                 xlabel: 'Date',
    #                 ylabel: 'Gage Height (ft.)',
    #                 colors: ["blue"],
    #                 strokeWidth: 2,
    #                 showRangeSelector: true
    #                 }
    #                 );
    #         </script>
    #         </body>
    #         </html>"""
    #         )
    #     super().save_model(request, obj, form, change)


class SponsorAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name"]


admin.site.register(SMSContribution, SMSContributionAdmin)
admin.site.register(InvalidSMSContribution, InvalidSMSContributionAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(Sponsor, SponsorAdmin)
