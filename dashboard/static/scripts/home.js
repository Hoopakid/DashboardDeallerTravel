const staff = document.querySelectorAll('.sidebar li')
// const all = document.querySelector('.all')

// let staffData = document.querySelector('input[name="staff"]');
let leaderboardData = document.querySelector('input[name="leaderboard"]');

// staffData = JSON.parse(staffData.value.replace(/'/g, '"'))
leaderboardData = JSON.parse(leaderboardData.value.replace(/'/g, '"'));

console.log(leaderboardData);

staff.forEach(i => {
    i.onclick = () => {
        staff.forEach(i => {
            i.dataset.selected = 'false';
        })
        i.dataset.selected = 'true';
        if (i.dataset.staff === "all") {
            document.querySelector('.all').style.display = 'block';
            document.querySelector('.staff').style.display = 'none';
        } else {
            document.querySelector('.staff h1').textContent = `${i.textContent}ning kunlik hisoboti`
            document.querySelector('.all').style.display = 'none';
            document.querySelector('.staff').style.display = 'flex';
            changeStaffInfo(i.textContent)
        }
    }
})

function changeStaffInfo(staff) {
    let data;
    leaderboardData.forEach(element => {
        if (element.responsible_user === staff) data = element;
        return;

    });
    document.getElementById('sales-count').textContent = data.sales_count
    document.getElementById('conversion').textContent = data.conversion + "%"
    document.getElementById('sales-price').textContent = data.sales_price
    document.getElementById('duration').textContent = data.call_average
    document.getElementById('call-out').textContent = data.call_out
    document.getElementById('call-in').textContent = data.call_in
    document.getElementById('coming-time').textContent = data.in_time
    document.getElementById('leaving-time').textContent = data.out_time
    document.getElementById('all-time').textContent = data.all_time

    var root = am5.Root.new("chartdiv");

    root.setThemes([
        am5themes_Animated.new(root)
    ]);

    var chart = root.container.children.push(am5xy.XYChart.new(root, {
        panX: true,
        panY: true,
        wheelX: "panX",
        wheelY: "zoomX",
        pinchZoomX: true,
        paddingLeft: 0,
        paddingRight: 1
    }));

    var cursor = chart.set("cursor", am5xy.XYCursor.new(root, {}));
    cursor.lineY.set("visible", false);


    var xRenderer = am5xy.AxisRendererX.new(root, {
        minGridDistance: 30,
        minorGridEnabled: true
    });

    xRenderer.labels.template.setAll({
        rotation: -90,
        centerY: am5.p50,
        centerX: am5.p100,
        paddingRight: 15
    });

    xRenderer.grid.template.setAll({
        location: 1
    })

    var xAxis = chart.xAxes.push(am5xy.CategoryAxis.new(root, {
        maxDeviation: 0.3,
        categoryField: "country",
        renderer: xRenderer,
        tooltip: am5.Tooltip.new(root, {})
    }));

    var yRenderer = am5xy.AxisRendererY.new(root, {
        strokeOpacity: 0.1
    })

    var yAxis = chart.yAxes.push(am5xy.ValueAxis.new(root, {
        maxDeviation: 0.3,
        renderer: yRenderer
    }));

    var series = chart.series.push(am5xy.ColumnSeries.new(root, {
        name: "Series 1",
        xAxis: xAxis,
        yAxis: yAxis,
        valueYField: "value",
        sequencedInterpolation: true,
        categoryXField: "country",
        tooltip: am5.Tooltip.new(root, {
            labelText: "{valueY}"
        })
    }));

    series.columns.template.setAll({cornerRadiusTL: 5, cornerRadiusTR: 5, strokeOpacity: 0});
    series.columns.template.adapters.add("fill", function (fill, target) {
        return chart.get("colors").getIndex(series.columns.indexOf(target));
    });

    series.columns.template.adapters.add("stroke", function (stroke, target) {
        return chart.get("colors").getIndex(series.columns.indexOf(target));
    });


    const dt = Object.entries(data.weekly).map(([day, val]) => {
        return {country: day, value: val}
    });
    xAxis.data.setAll(dt);
    series.data.setAll(dt);

    series.appear(1000);
    chart.appear(1000, 100);
}
am5.ready(function () {


});
