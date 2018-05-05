
		var barChartData = {
			labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
			datasets: [{
				label: 'Open Tickets',
				backgroundColor: "#3e95cd",
				data: [
					25,
                    20,
                    17,
                    12,
                    16,
                    9,
                    5,
                    1
					
				]
			}, {
				label: 'In Progress',
				backgroundColor: "#42b3f4" ,
				data: [
                    5,
                    1,
                    2,
                    3,
                    5,
                    1,

				]
			}, {
				label: 'Closed Tickets',
				backgroundColor: "#9CC366",
				data: [
                    0,
                    2,
                    3,
                    2,
                    2,
                    3,
                    4
				]
			}]

		};
	  function create_chart() {
			var ctx = document.getElementById('myChart').getContext('2d');
			window.myBar = new Chart(ctx, {
				type: 'bar',
				data: barChartData,
				options: {
					title: {
						display: true,
						text: 'Chart.js Bar Chart - Stacked'
					},
					tooltips: {
						mode: 'index',
						intersect: false
					},
					responsive: true,
					scales: {
						xAxes: [{
							stacked: true,
						}],
						yAxes: [{
							stacked: true
						}]
					}
				}
			});
		};

		
			
		
	