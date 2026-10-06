// Bilateral filter (spatial = 3, range = 50, on an 8-bit copy): Fiji command "Bilateral Filter"
// Part of the CiliaAI mini-course: https://github.com/juglab/CiliaAI-minicourse
// Run in Fiji via Plugins > Macros > Run... and select data/convollaria.tif when asked.
// Shows a 256 x 256 crop of the raw image (left) next to the result (right).

open(File.openDialog("Select data/convollaria.tif"));
run("Properties...", "unit=pixel pixel_width=1 pixel_height=1 voxel_depth=1");
makeRectangle(400, 500, 256, 256); run("Crop"); run("Select None"); rename("raw");
setMinAndMax(350, 1300); run("Set... ", "zoom=200"); setLocation(30, 120);
run("Duplicate...", "title=work"); setMinAndMax(350, 1300); run("8-bit");
run("Bilateral Filter", "spatial=3 range=50");
rename("denoised");
selectWindow("work"); close(); selectWindow("denoised");
setMinAndMax(0, 255); run("Set... ", "zoom=200"); setLocation(580, 120);
