<script setup>
import { ref, onMounted } from 'vue';
import Chart from 'primevue/chart';
import axios from 'axios';

const rainChartData = ref(null);
const soilChartData = ref(null);
const chartOptions = ref(null);
const rainChartOptions = ref(null);
const soilChartOptions = ref(null);
const isLoading = ref(true);

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
                // Handle different MongoDB BSON date formats
                let dateStr;
                if (d['BSON UTC'].$date) {
                    // Handle ISODate format
                    if (typeof d['BSON UTC'].$date === 'string') {
                        dateStr = d['BSON UTC'].$date;
                    } else if (d['BSON UTC'].$date.$numberLong) {
                        // Handle timestamp in milliseconds
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

        console.log('Raw BSON UTC values:', recentData.map(d => d['BSON UTC'])); // Debug log
        console.log('Parsed timestamps:', timestamps);

        const rainValues = recentData.map(d => d.rain_value);
        const soilMoistures = recentData.map(d => d.soil_moisture);
        const pumpStatus = recentData.map(d => d.soil_pump ? 1 : 0);

        console.log('Timestamps:', timestamps);
        console.log('Rain values:', rainValues);
        console.log('Soil moistures:', soilMoistures);
        console.log('Pump status:', pumpStatus);

        const documentStyle = getComputedStyle(document.documentElement);
        const textColor = documentStyle.getPropertyValue('--text-color');
        const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
        const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

        // Base chart options
        chartOptions.value = {
            maintainAspectRatio: false,
            aspectRatio: 0.8,
            plugins: {
                legend: {
                    labels: {
                        color: textColor
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            if (context.dataset.label === 'Pump Status') {
                                return `Pump: ${context.raw === 1 ? 'ON' : 'OFF'}`;
                            }
                            return `${context.dataset.label}: ${context.raw}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: textColorSecondary
                    },
                    grid: {
                        color: surfaceBorder
                    }
                }
            }
        };

        // Rain chart options
        rainChartOptions.value = {
            ...chartOptions.value,
            scales: {
                ...chartOptions.value.scales,
                y: {
                    beginAtZero: true,
                    max: 4096,
                    ticks: {
                        color: textColorSecondary,
                        stepSize: 500
                    },
                    grid: {
                        color: surfaceBorder
                    }
                }
            }
        };

        // Soil chart options
        soilChartOptions.value = {
            ...chartOptions.value,
            scales: {
                ...chartOptions.value.scales,
                y: {
                    beginAtZero: true,
                    max: 4096,
                    ticks: {
                        color: textColorSecondary,
                        stepSize: 500
                    },
                    grid: {
                        color: surfaceBorder
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    min: 0,
                    max: 1,
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            return value === 1 ? 'ON' : 'OFF';
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            }
        };

        // Rain Value Chart Configuration
        rainChartData.value = {
            labels: timestamps,
            datasets: [
                {
                    label: 'Rain Value',
                    data: rainValues,
                    fill: false,
                    borderColor: documentStyle.getPropertyValue('--teal-500'),
                    tension: 0.4,
                    backgroundColor: documentStyle.getPropertyValue('--teal-500')
                }
            ]
        };

        // Soil Moisture and Pump Status Chart Configuration
        soilChartData.value = {
            labels: timestamps,
            datasets: [
                {
                    type: 'bar',
                    label: 'Soil Moisture',
                    data: soilMoistures,
                    backgroundColor: documentStyle.getPropertyValue('--purple-500'),
                    borderColor: documentStyle.getPropertyValue('--purple-500'),
                    order: 1,
                    yAxisID: 'y'
                },
                {
                    type: 'line',
                    label: 'Pump Status',
                    data: pumpStatus,
                    borderColor: documentStyle.getPropertyValue('--red-500'),
                    backgroundColor: documentStyle.getPropertyValue('--red-500'),
                    borderWidth: 2,
                    order: 0,
                    yAxisID: 'y1'
                }
            ]
        };
        
        isLoading.value = false;
    } catch (error) {
        console.error('Error fetching sensor data:', error);
        isLoading.value = false;
    }
}

onMounted(() => {
    fetchSensorData();
    // Refresh data every minute
    setInterval(fetchSensorData, 60000);
});
</script>

<template>
    <div class="grid">
        <div v-if="isLoading" class="col-12 flex justify-center items-center">
            <div class="text-xl">Loading sensor data...</div>
        </div>
        
        <template v-else>
            <!-- Rain Value Chart -->
            <div class="col-12 xl:col-6">
                <div class="card">
                    <h3>Rain Value Over Time</h3>
                    <Chart 
                        type="line" 
                        :data="rainChartData" 
                        :options="rainChartOptions"
                        class="h-30rem"
                    />
                </div>
            </div>

            <!-- Soil Moisture and Pump Status Chart -->
            <div class="col-12 xl:col-6">
                <div class="card">
                    <h3>Soil Moisture and Pump Status</h3>
                    <Chart 
                        type="bar" 
                        :data="soilChartData" 
                        :options="soilChartOptions"
                        class="h-30rem"
                    />
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

h3 {
    margin-bottom: 1.5rem;
    font-weight: 600;
}
</style>