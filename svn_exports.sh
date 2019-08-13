base_url=http://192.168.1.21:18080/svn
repos=(
	UBOX_STEAM
	UBOX_CYTM
	UBOX_YLXY
	UBOX_STORY
	UBOX_ENGLISH
	UBOX_GAMEMATCH
	UBOX_SPORTS
)

for repo in ${repos[@]}; do
	if [[ ! -d ${repo} ]]; then
		mkdir -p $repo;
		for branch in $(svn ls "${base_url}/${repo}"); do
			cd $repo;
			git svn clone ${base_url}/${repo}/${branch} -r HEAD;
			cd ..;
		done
	else
		echo "${repo} already existed."
	fi
done
