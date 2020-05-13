let endpoint = '/api/data/'

let binanceChartInitialized = false;

class Currency {
    data = []
    labels = []
    constructor(symbol) {
        this.symbol = symbol
    }
}

getDataContainers = function() {
    const symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'BNBUSDT']
    let dataContainers = []

    symbols.forEach(function (symbol) {
        dataContainers.push(new Currency(symbol))
    });

    return dataContainers;
}


$(document).ready(function(){

    let timeSpan = $("input[name='timespan']:checked").val();
    getData(timeSpan);

    $("input[type='radio']").change(function(){
        timeSpan = $("input[name='timespan']:checked").val();
        if(timeSpan){
            getData(timeSpan);
        }
    });
});

getData = function(timeSpan) {

    let interval = "5m";
    let date_start = new Date(new Date().setDate(new Date().getDate() - 1)).toUTCString();
    switch(timeSpan){
        case '1d':
            break;
        case '1w':
            interval = "1h";
            date_start = new Date(new Date().setDate(new Date().getDate() - 7)).toUTCString();
            break;
        case '6m':
            interval = "1d";
            date_start = new Date(new Date().setMonth(new Date().getMonth() - 6)).toUTCString();
            break;
        case 'y':
            interval = "1d";
            date_start = new Date(new Date().setFullYear(new Date().getFullYear() - 1)).toUTCString();
            break;
    }

    let dataContainers = getDataContainers();

    let promises = []

    dataContainers.forEach(function (container) {
        let request = $.ajax({
            method: "GET",
            url: endpoint,
            data: {
                symbol: container.symbol,
                interval: interval,
                date_start: date_start
            },
            success: function(data){
                for(let i = 0; i < data.length; i++)
                {
                    container.data.push(Number(data[i].open));
                    date = new Date(data[i].open_time);
                    container.labels.push(date.toFormat(interval));
                }
            },
            error: function(error_data){
            }
        });

        promises.push(request);
    });

    $.when.apply(null, promises).done(function(){
        drawChart(dataContainers);
     })
}

drawChart = function(dataContainers) {
    if(binanceChartInitialized == true){
        binanceChart.destroy();
    }
    let ctx = document.getElementById('binanceChart').getContext('2d');
    binanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dataContainers[0].labels,
            datasets:[{
                data: dataContainers[0].data,
                label: "BTC",
                fill: false,
                borderWidth: 2,
                pointStyle: 'line',
                hidden: false,
                borderColor: 'rgba(255, 0, 0, 0.6)'
            },
            {
                data: dataContainers[1].data,
                label: "ETH",
                fill: false,
                borderWidth: 2,
                pointStyle: 'line',
                hidden: true,
                borderColor: 'rgba(44, 130, 201, 1)'
            },
            {
                data: dataContainers[2].data,
                label: "LTC",
                fill: false,
                borderWidth: 2,
                pointStyle: 'line',
                hidden: true,
                borderColor: 'rgba(245, 229, 27, 1)'
            },
            {
                data: dataContainers[3].data,
                label: "BNB",
                fill: false,
                borderWidth: 2,
                pointStyle: 'line',
                hidden: true,
                borderColor: 'rgba(54, 215, 183, 1)'
            }]
        },
        options: {
            title: {
                display: true,
                text: 'Binance',
                fontColor: 'rgba(0, 0, 0, 0.6)',
                fontSize: 20
            },
            legend: {
                labels: {
                    fontColor: 'rgb(255, 99, 132)',
                    fontSize: 15
                }
            },
            scales: {
                xAxes: [{
                    ticks: {
                        callback: function (tick, index, array) {
                            return (index % 4) ? "" : tick;
                        }
                    }
                }]
            }
        }
    });
    $('#binanceChart').css("visibility", "visible");
    binanceChartInitialized = true;
}

Date.prototype.toFormat = function(interval) {

    let month_names =["Jan","Feb","Mar",
                      "Apr","May","Jun",
                      "Jul","Aug","Sep",
                      "Oct","Nov","Dec"];

    let day = this.getDate();
    let month_index = this.getMonth();
    let year = this.getFullYear();

    let hour = this.getHours();
    let minutes = this.getMinutes();
    minutes = (minutes < 10 ? "0" : "") + minutes;
    let timeOfDay = (hour < 12) ? "AM" : "PM";

    let str = "";

    switch(interval){
        case "5m":
            str = "" + hour + ":" + minutes + " " + timeOfDay;
            break;
        case "1h":
            str = "" + hour + ":" + minutes + " " + timeOfDay + " " + day + " " + month_names[month_index];
            break;
        default:
            str =  "" + day + " " + month_names[month_index] + " " + year;
            break;
    }

    return str;
}