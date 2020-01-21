annots=(
/media/dh/HDD1/pp/Labrador200/annotations/trimmed_annotations_1.xml
/media/dh/HDD1/pp/Labrador200/annotations/trimmed_annotations_2.xml
/media/dh/HDD1/pp/Labrador200/annotations/trimmed_annotations_3.xml
/media/dh/HDD1/pp/Labrador200/annotations/trimmed_annotations_4.xml
/media/dh/HDD1/pp/Labrador200/annotations/trimmed_annotations_5.xml
)

root="/media/dh/HDD1/pp/Labrador200/trimmed"
out="/media/dh/HDD1/pp/Labrador200/dh_format"
sample=1

for xml_file in "${annots[@]}"
do	
	echo "Converting $xml_file now.."
	python3 convert.py --xml $xml_file --root $root --out $out --sample 1
done


