try {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class SoundVolume {
    [DllImport("winmm.dll")]
    public static extern int waveOutSetVolume(IntPtr hwo, uint dwVolume);

    public static void SetVolumePercent(int percent) {
        uint volume = (uint)((ushort)Math.Round(percent / 100.0 * 0xFFFF));
        uint fullVolume = volume | (volume << 16);
        int result = waveOutSetVolume(IntPtr.Zero, fullVolume);
        System.Console.WriteLine("WaveOut Result: " + result);
    }
}
'@
    [SoundVolume]::SetVolumePercent(100)
    Write-Output "Volume set to 100 SUCCESS"
} catch {
    Write-Output "Error: $_"
}
