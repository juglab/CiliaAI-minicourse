// Kuwahara filter (edge-preserving smoothing): Fiji command "Kuwahara Filter"
// Part of the CiliaAI mini-course: https://github.com/juglab/CiliaAI-minicourse
// Run in Fiji via Plugins > Macros > Run... and select data/convollaria.tif when asked.
// Shows a 256 x 256 crop of the raw image (left) next to the result (right).

open(File.openDialog("Select data/convollaria.tif"));
run("Properties...", "unit=pixel pixel_width=1 pixel_height=1 voxel_depth=1");
makeRectangle(400, 500, 256, 256); run("Crop"); run("Select None"); rename("raw");
setMinAndMax(350, 1300); run("Set... ", "zoom=200"); setLocation(30, 120);
run("Duplicate...", "title=work");
run("Kuwahara Filter", " ");
rename("denoised");
resetMinAndMax(); setMinAndMax(350, 1300); run("Set... ", "zoom=200"); setLocation(580, 120);
