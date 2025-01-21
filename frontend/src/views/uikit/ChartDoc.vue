<script setup>
import { useLayout } from '@/layout/composables/layout';
import { onMounted, ref, watch } from 'vue';
import axios from 'axios';


const { getPrimary, getSurface, isDarkTheme } = useLayout();
const lineData = ref(null);
const pieData = ref(null);
const polarData = ref(null);
const barData = ref(null);
const radarData = ref(null);
const lineOptions = ref(null);
const pieOptions = ref(null);
const polarOptions = ref(null);
const barOptions = ref(null);
const radarOptions = ref(null);
const isLoading = ref(true);
const predictionData = ref(null);
const predictionOptions = ref(null);

onMounted(() => {
    setColorOptions();
});

function setColorOptions() {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--text-color');
    const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
    const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

    barData.value = {
        labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
        datasets: [
            {
                label: 'My First dataset',
                backgroundColor: documentStyle.getPropertyValue('--p-primary-500'),
                borderColor: documentStyle.getPropertyValue('--p-primary-500'),
                data: [65, 59, 80, 81, 56, 55, 40]
            },
            {
                label: 'My Second dataset',
                backgroundColor: documentStyle.getPropertyValue('--p-primary-200'),
                borderColor: documentStyle.getPropertyValue('--p-primary-200'),
                data: [28, 48, 40, 19, 86, 27, 90]
            }
        ]
    };
    barOptions.value = {
        plugins: {
            legend: {
                labels: {
                    fontColor: textColor
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    color: textColorSecondary,
                    font: {
                        weight: 500
                    }
                },
                grid: {
                    display: false,
                    drawBorder: false
                }
            },
            y: {
                ticks: {
                    color: textColorSecondary
                },
                grid: {
                    color: surfaceBorder,
                    drawBorder: false
                }
            }
        }
    };

    pieData.value = {
        labels: ['A', 'B', 'C'],
        datasets: [
            {
                data: [540, 325, 702],
                backgroundColor: [documentStyle.getPropertyValue('--p-indigo-500'), documentStyle.getPropertyValue('--p-purple-500'), documentStyle.getPropertyValue('--p-teal-500')],
                hoverBackgroundColor: [documentStyle.getPropertyValue('--p-indigo-400'), documentStyle.getPropertyValue('--p-purple-400'), documentStyle.getPropertyValue('--p-teal-400')]
            }
        ]
    };

    pieOptions.value = {
        plugins: {
            legend: {
                labels: {
                    usePointStyle: true,
                    color: textColor
                }
            }
        }
    };

    lineData.value = {
        labels: [],
        datasets: [
            {
                label: 'Soil Moisture',
                data: [],
                fill: false,
                backgroundColor: documentStyle.getPropertyValue('--p-primary-500'),
                borderColor: documentStyle.getPropertyValue('--p-primary-500'),
                tension: 0.4,
                pointStyle: 'circle',
                pointRadius: 5,
                pointHoverRadius: 8
            }
        ]
    };

    lineOptions.value = {
        maintainAspectRatio: false,
        aspectRatio: 0.8,
        plugins: {
            legend: {
                labels: {
                    color: textColor,
                    font: {
                        weight: 500
                    }
                }
            },
            tooltip: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function(context) {
                        return `Soil Moisture: ${context.raw}`;
                    }
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    color: textColorSecondary,
                    font: {
                        weight: 500
                    }
                },
                grid: {
                    color: surfaceBorder,
                    drawBorder: false
                }
            },
            y: {
                beginAtZero: true,
                max: 4096,
                ticks: {
                    color: textColorSecondary,
                    font: {
                        weight: 500
                    },
                    stepSize: 500
                },
                grid: {
                    color: surfaceBorder,
                    drawBorder: false
                },
                title: {
                    display: true,
                    text: 'Soil Moisture Level',
                    color: textColor,
                    font: {
                        weight: 500
                    }
                }
            }
        }
    };

    polarData.value = {
        datasets: [
            {
                data: [11, 16, 7, 3],
                backgroundColor: [documentStyle.getPropertyValue('--p-indigo-500'), documentStyle.getPropertyValue('--p-purple-500'), documentStyle.getPropertyValue('--p-teal-500'), documentStyle.getPropertyValue('--p-orange-500')],
                label: 'My dataset'
            }
        ],
        labels: ['Indigo', 'Purple', 'Teal', 'Orange']
    };

    polarOptions.value = {
        plugins: {
            legend: {
                labels: {
                    color: textColor
                }
            }
        },
        scales: {
            r: {
                grid: {
                    color: surfaceBorder
                }
            }
        }
    };

    radarData.value = {
        labels: ['Eating', 'Drinking', 'Sleeping', 'Designing', 'Coding', 'Cycling', 'Running'],
        datasets: [
            {
                label: 'My First dataset',
                borderColor: documentStyle.getPropertyValue('--p-indigo-400'),
                pointBackgroundColor: documentStyle.getPropertyValue('--p-indigo-400'),
                pointBorderColor: documentStyle.getPropertyValue('--p-indigo-400'),
                pointHoverBackgroundColor: textColor,
                pointHoverBorderColor: documentStyle.getPropertyValue('--p-indigo-400'),
                data: [65, 59, 90, 81, 56, 55, 40]
            },
            {
                label: 'My Second dataset',
                borderColor: documentStyle.getPropertyValue('--p-purple-400'),
                pointBackgroundColor: documentStyle.getPropertyValue('--p-purple-400'),
                pointBorderColor: documentStyle.getPropertyValue('--p-purple-400'),
                pointHoverBackgroundColor: textColor,
                pointHoverBorderColor: documentStyle.getPropertyValue('--p-purple-400'),
                data: [28, 48, 40, 19, 96, 27, 100]
            }
        ]
    };

    radarOptions.value = {
        plugins: {
            legend: {
                labels: {
                    fontColor: textColor
                }
            }
        },
        scales: {
            r: {
                grid: {
                    color: textColorSecondary
                }
            }
        }
    };
}

async function fetchSensorData() {
    try {
        const response = await axios.get('http://localhost:5000/sensor_data');
        const sensorData = response.data;
        
        console.log('Received sensor data:', sensorData);
        
        if (!sensorData || sensorData.length === 0) {
            console.warn('No sensor data received');
            return;
        }
        
        // Get last 10 readings and reverse them for chronological order
        const recentData = sensorData.slice(-10).reverse();
        console.log('Recent data:', recentData);
        
        // Fix timestamp parsing from MongoDB BSON format
        const timestamps = recentData.map(d => {
            try {
                let dateStr;
                if (d['BSON UTC'].$date) {
                    if (typeof d['BSON UTC'].$date === 'string') {
                        dateStr = d['BSON UTC'].$date;
                    } else if (d['BSON UTC'].$date.$numberLong) {
                        dateStr = parseInt(d['BSON UTC'].$date.$numberLong);
                    }
                } else {
                    dateStr = d['BSON UTC'];
                }
                
                const date = new Date(dateStr);
                if (isNaN(date.getTime())) {
                    console.error('Invalid date:', d['BSON UTC']);
                    return 'Invalid Date';
                }
                return date.toLocaleTimeString();
            } catch (error) {
                console.error('Error parsing date:', error, d['BSON UTC']);
                return 'Invalid Date';
            }
        });

        const soilMoistureValues = recentData.map(d => d.soil_moisture);
        
        const documentStyle = getComputedStyle(document.documentElement);
        
        // Update line chart data
        lineData.value = {
            labels: timestamps,
            datasets: [
                {
                    label: 'Soil Moisture',
                    data: soilMoistureValues,
                    fill: false,
                    backgroundColor: documentStyle.getPropertyValue('--p-primary-500'),
                    borderColor: documentStyle.getPropertyValue('--p-primary-500'),
                    tension: 0.4,
                    pointStyle: 'circle',
                    pointRadius: 5,
                    pointHoverRadius: 8
                }
            ]
        };
        
        // Update pie chart for soil moisture distribution
        const moistureRanges = {
            low: 0,
            medium: 0,
            high: 0
        };
        
        recentData.forEach(reading => {
            if (reading.soil_moisture < 1500) moistureRanges.low++;
            else if (reading.soil_moisture < 2000) moistureRanges.medium++;
            else moistureRanges.high++;
        });
        
        pieData.value = {
            labels: ['Low Moisture', 'Medium Moisture', 'High Moisture'],
            datasets: [
                {
                    data: [moistureRanges.low, moistureRanges.medium, moistureRanges.high],
                    backgroundColor: [
                        documentStyle.getPropertyValue('--p-red-500'),
                        documentStyle.getPropertyValue('--p-yellow-500'),
                        documentStyle.getPropertyValue('--p-green-500')
                    ],
                    hoverBackgroundColor: [
                        documentStyle.getPropertyValue('--p-red-400'),
                        documentStyle.getPropertyValue('--p-yellow-400'),
                        documentStyle.getPropertyValue('--p-green-400')
                    ]
                }
            ]
        };
        
        isLoading.value = false;
    } catch (error) {
        console.error('Error fetching sensor data:', error);
        isLoading.value = false;
    }
}

async function fetchPredictions() {
    try {
        const response = await axios.get('http://localhost:5000/moisture_predictions');
        const predictions = response.data;
        
        if (!predictions || predictions.length === 0) {
            console.warn('No predictions received');
            return;
        }
        
        const timestamps = predictions.map(p => {
            const date = new Date(p.timestamp);
            return date.toLocaleTimeString();
        });
        
        const moistureValues = predictions.map(p => p.predicted_moisture);
        
        const documentStyle = getComputedStyle(document.documentElement);
        
        predictionData.value = {
            labels: timestamps,
            datasets: [
                {
                    label: 'Predicted Soil Moisture',
                    data: moistureValues,
                    fill: false,
                    backgroundColor: documentStyle.getPropertyValue('--p-orange-500'),
                    borderColor: documentStyle.getPropertyValue('--p-orange-500'),
                    tension: 0.4,
                    pointStyle: 'circle',
                    pointRadius: 5,
                    pointHoverRadius: 8
                }
            ]
        };
        
        predictionOptions.value = {
            maintainAspectRatio: false,
            aspectRatio: 0.8,
            plugins: {
                legend: {
                    labels: {
                        color: textColor,
                        font: {
                            weight: 500
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `Predicted Moisture: ${context.raw.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: textColorSecondary,
                        font: {
                            weight: 500
                        }
                    },
                    grid: {
                        color: surfaceBorder,
                        drawBorder: false
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 4096,
                    ticks: {
                        color: textColorSecondary,
                        font: {
                            weight: 500
                        },
                        stepSize: 500
                    },
                    grid: {
                        color: surfaceBorder,
                        drawBorder: false
                    },
                    title: {
                        display: true,
                        text: 'Predicted Soil Moisture Level',
                        color: textColor,
                        font: {
                            weight: 500
                        }
                    }
                }
            }
        };
    } catch (error) {
        console.error('Error fetching predictions:', error);
    }
}

onMounted(() => {
    setColorOptions();
    fetchSensorData();
    fetchPredictions();
    // Refresh data every minute
    setInterval(() => {
        fetchSensorData();
        fetchPredictions();
    }, 60000);
});

watch(
    [getPrimary, getSurface, isDarkTheme],
    () => {
        setColorOptions();
    },
    { immediate: true }
);
</script>

<template>
    <div class="grid grid-cols-12 gap-8">
        <div v-if="isLoading" class="col-span-12 flex justify-center items-center">
            <div class="text-xl">Loading sensor data...</div>
        </div>
        
        <template v-else>
            <div class="col-span-12 xl:col-span-6">
                <div class="card">
                    <div class="font-semibold text-xl mb-4">Soil Moisture Trend</div>
                    <Chart type="line" :data="lineData" :options="lineOptions"></Chart>
                </div>
            </div>
            
            <div class="col-span-12 xl:col-span-6">
                <div class="card">
                    <div class="font-semibold text-xl mb-4">Moisture Level Distribution</div>
                    <Chart type="pie" :data="pieData" :options="pieOptions"></Chart>
                </div>
            </div>
            
            <div class="col-span-12">
                <div class="card">
                    <div class="font-semibold text-xl mb-4">24-Hour Soil Moisture Predictions</div>
                    <div class="mb-4 text-sm text-gray-600">
                        Predictions based on Random Forest model trained on historical data
                    </div>
                    <Chart v-if="predictionData" type="line" :data="predictionData" :options="predictionOptions"></Chart>
                    <div v-else class="text-center py-4 text-gray-500">Loading predictions...</div>
                </div>
            </div>
        </template>
    </div>
</template>

<style scoped>
.card {
    background: var(--surface-card);
    padding: 1.5rem;
    border-radius: 10px;
    margin-bottom: 1rem;
}
</style>
